from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from .models.item import ItemImage
from .models import Item, Review
from orders.models import Order  
from .serializers import (
    ItemListSerializer, ItemDetailSerializer, ItemCreateUpdateSerializer,
    ReviewSerializer, ReviewCreateUpdateSerializer, ItemImageSerializer
)

'''
PAGE-SPECIFIC ENDPOINTS:
├── HomepageView
├── ItemViewSet
├── ReviewView
└── MyReviewableItemsView
'''

# Homepage view
class HomepageView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        trending = Item.get_trending_items()
        featured = Item.get_featured_items()
        recently_viewed = Item.get_recently_viewed(request, limit=10)
        recommendations = Item.get_recommendations(request, limit=10)

        return Response({
            'trending': ItemListSerializer(trending, many=True).data,
            'featured': ItemListSerializer(featured, many=True).data,
            'recently_viewed': ItemListSerializer(recently_viewed, many=True).data,
            'recommended': ItemListSerializer(recommendations, many=True).data,
            'categories': Item.get_all_categories(),
        })

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    permission_classes = [AllowAny]
    # lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'list':
            return ItemListSerializer
        elif self.action == 'retrieve':
            return ItemDetailSerializer
        else:
            return ItemCreateUpdateSerializer
    
    def create(self, request, *args, **kwargs):
        images = request.FILES.getlist('images')
        image_urls = request.data.getlist('image_urls', [])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.save()
        # Handle uploaded files
        for image in images:
            ItemImage.objects.create(item=item, image_file=image)
        # Handle URLs
        for url in image_urls:
            if url:
                ItemImage.objects.create(item=item, image_url=url)
        read_serializer = self.get_serializer(item)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        item = serializer.save()
        images = request.FILES.getlist('images')
        image_urls = request.data.getlist('image_urls', [])
        if images or image_urls:
            # Optionally clear old images
            item.item_images.all().delete()
            for image in images:
                ItemImage.objects.create(item=item, image_file=image)
            for url in image_urls:
                if url:
                    ItemImage.objects.create(item=item, image_url=url)
        read_serializer = self.get_serializer(item)
        return Response(read_serializer.data)

    def get_queryset(self):
        # Special case: user's own items
        if (self.request.query_params.get('seller') == 'me' and 
            self.request.user.is_authenticated):
            return Item.objects.filter(seller=self.request.user)
        # Use model method for everything else
        return Item.search_items(
            query=self.request.query_params.get('search'),
            category=self.request.query_params.get('category'),
            min_price=self.request.query_params.get('min_price'),
            max_price=self.request.query_params.get('max_price'),
            condition=self.request.query_params.get('condition'),
            is_on_sale=self.request.query_params.get('is_on_sale'),
            is_featured=self.request.query_params.get('is_featured'),
            min_rating=self.request.query_params.get('min_rating')
        )

    @action(detail=True, methods=['get'])
    def suggestions(self, request, pk=None):
        """GET /items/{id}/suggestions/ - Get recommendations, related, seller's other items, and best sellers in category"""
        item = self.get_object()

        # Other items in the same category (excluding current item)
        related = Item.objects.filter(
            item_category=item.display_category
        ).exclude(id=item.id)[:8]
        # Other items from the same seller (excluding current item)
        seller_items = Item.objects.filter(
            seller=item.seller
        ).exclude(id=item.id)[:8]
        # Best sellers in the same category (excluding current item)
        best_sellers_by_category = Item.get_best_sellers_by_category(
            items_each_category=8,
            max_categories=1
        )
        best_sellers = best_sellers_by_category.get(item.display_category, [])
        best_sellers = [i for i in best_sellers if i.id != item.id]
    
        return Response({
            'related': ItemListSerializer(related, many=True, context={'request': request}).data,
            'seller_items': ItemListSerializer(seller_items, many=True, context={'request': request}).data,
            'best_sellers_in_category': ItemListSerializer(best_sellers, many=True, context={'request': request}).data,
        })

# ==================== REVIEW ENDPOINTS ====================

class ReviewView(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]

    def post(self, request, item_id):
        """POST /items/{item_id}/reviews/ - Create new review for an item"""
        #  Later be item = get_object_or_404(Item, slug=item_slug)
        item = get_object_or_404(Item, id=item_id)
        serializer = ReviewCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            order_id = serializer.validated_data.get('order_id')
            order = get_object_or_404(Order, id=order_id) if order_id else None
            review = serializer.save(
                reviewer=request.user,
                item=item,
                order=order,
                media=request.media,
            )
            response_serializer = ReviewSerializer(review)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, review_id):
        """PUT /reviews/{review_id}/ - Update existing review"""
        review = get_object_or_404(Review, id=review_id, reviewer=request.user)
        serializer = ReviewCreateUpdateSerializer(review, data=request.data)
        if serializer.is_valid():
            updated_review = serializer.save()
            response_serializer = ReviewSerializer(updated_review)
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, review_id):
        """PATCH /reviews/{review_id}/ - Partially update existing review"""
        review = get_object_or_404(Review, id=review_id, reviewer=request.user)
        serializer = ReviewCreateUpdateSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            updated_review = serializer.save()
            response_serializer = ReviewSerializer(updated_review)
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, review_id):
        """DELETE /reviews/{review_id}/ - Delete existing review"""
        review = get_object_or_404(Review, id=review_id, reviewer=request.user)
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def upvote(self, request, pk=None):
        review = get_object_or_404(Review, id=pk)
        user = request.user
        if review.upvoted_by.filter(id=user.id).exists():
            review.helpful_count -= 1
            review.upvoted_by.remove(user)
            is_upvoted = False
        else:
            review.helpful_count += 1
            review.upvoted_by.add(user)
            is_upvoted = True
        review.save()
        return Response({
            'helpful_count': review.helpful_count,
            'is_upvoted': is_upvoted
        }, status=status.HTTP_200_OK)

class MyReviewableItemsView(APIView):
    def get(self, request):
        """GET /my-reviewable-items/ - List items user can review"""
        user_orders = Order.objects.filter(
            user=request.user,
            status__in=['completed', 'delivered']
        )
        reviewable_items = []
        for order in user_orders:
            for item in order.items.all():
                if not Review.objects.filter(order=order, item=item).exists():
                    reviewable_items.append({
                        'item': ItemListSerializer(item).data,
                        'order_id': order.id,
                        'order_date': order.created_at,
                    })
        return Response(reviewable_items)