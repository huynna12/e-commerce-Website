# views.py
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView

from .models.item import ItemImage

from .models import Item, Review
from orders.models import Order  
from .serializers import (
    ItemListSerializer, ItemDetailSerializer, ItemCreateUpdateSerializer,
    ReviewSerializer, ReviewCreateUpdateSerializer
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

    def get_serializer_class(self):
        if self.action == 'list':
            return ItemListSerializer
        elif self.action == 'retrieve':
            return ItemDetailSerializer
        else:
            return ItemCreateUpdateSerializer
    
    def create(self, request, *args, **kwargs):
        images = request.FILES.getlist('images')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.save()
        for image in images:
            ItemImage.objects.create(item=item, image=image)
        read_serializer = self.get_serializer(item)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)
    
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
    def reviews(self, request, pk=None):
        """GET /items/{id}/reviews/ - List reviews for an item"""
        item = self.get_object()
        reviews = Review.objects.filter(item=item).order_by('-created_at')
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def increment_view(self, request, pk=None):
        """POST /items/{id}/increment_view/ - Increment item view count"""
        item = self.get_object()
        new_count = item.increment_view_count()
        return Response({'view_count': new_count})

    @action(detail=False, methods=['get'])
    def trending(self, request):
        limit = int(request.GET.get('limit', 10))
        items = Item.get_trending_items(limit=limit)
        serializer = ItemListSerializer(items, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def categories(self, request):
        categories = Item.get_all_categories()
        return Response({'categories': categories})

    @action(detail=False, methods=['get'])
    def best_sellers(self, request):
        items_per_category = int(request.GET.get('items_per_category', 5))
        max_categories = int(request.GET.get('max_categories', 6))
        best_sellers = Item.get_best_sellers_by_category(
            items_each_category=items_per_category,
            max_categories=max_categories
        )
        result = {}
        for category_name, items in best_sellers.items():
            result[category_name] = ItemListSerializer(items, many=True).data
        return Response(result)

    @action(detail=False, methods=['get'])
    def homepage_recommendations(self, request):
        """GET /items/homepage-recommendations/ - Get recommended items for homepage"""
        limit = int(request.GET.get('limit', 10))
        items = Item.get_recommendations(request, limit=limit)
        serializer = ItemListSerializer(items, many=True)
        return Response(serializer.data)

# ==================== REVIEW ENDPOINTS ====================

class ReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, item_id):
        """POST /items/{item_id}/reviews/ - Create new review for an item"""
        item = get_object_or_404(Item, id=item_id)
        serializer = ReviewCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            order_id = serializer.validated_data.get('order_id')
            order = get_object_or_404(Order, id=order_id) if order_id else None
            review = serializer.save(
                reviewer=request.user,
                item=item,
                order=order
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

class MyReviewableItemsView(APIView):
    permission_classes = [IsAuthenticated]

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
