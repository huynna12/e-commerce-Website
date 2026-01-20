from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django.apps import apps
from .models.item import ItemImage
from .models import Item, Review
from orders.models import Order  
from .serializers import (
    ItemListSerializer, ItemDetailSerializer, ItemCreateUpdateSerializer,
    ReviewSerializer, ReviewCreateUpdateSerializer, ItemImageSerializer
)
from .permissions import IsSellerOrReadOnly

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
        recently_viewed = Item.get_recently_viewed(request, limit=10)
        recommendations = Item.get_recommendations(request, limit=10)

        return Response({
            'trending': ItemListSerializer(trending, many=True).data,
            'recently_viewed': ItemListSerializer(recently_viewed, many=True).data,
            'recommended': ItemListSerializer(recommendations, many=True).data,
            'categories': Item.get_all_categories(),
        })

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()

    permission_classes = [IsSellerOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ItemListSerializer
        elif self.action == 'retrieve':
            return ItemDetailSerializer
        else:
            return ItemCreateUpdateSerializer
    
    def create(self, request, *args, **kwargs):
        images = request.FILES.getlist('images')
        if hasattr(request.data, 'getlist'):
            image_urls = request.data.getlist('image_urls')
        else:
            image_urls = request.data.get('image_urls') or []
            if not isinstance(image_urls, list):
                image_urls = [image_urls]

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.save(seller=request.user)

        images_data = [{'image_file': f} for f in images] + [
            {'image_url': u} for u in image_urls if str(u).strip()
        ]
        serializer._set_images(item, images_data)

        read_serializer = self.get_serializer(item)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        images = request.FILES.getlist('images')
        if hasattr(request.data, 'getlist'):
            image_urls = request.data.getlist('image_urls')
        else:
            image_urls = request.data.get('image_urls') or []
            if not isinstance(image_urls, list):
                image_urls = [image_urls]

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        item = serializer.save()

        if images or image_urls:
            images_data = [{'image_file': f} for f in images] + [
                {'image_url': u} for u in image_urls if str(u).strip()
            ]
            serializer._set_images(item, images_data)

        read_serializer = self.get_serializer(item)
        return Response(read_serializer.data)

    def get_queryset(self):
        # Special case: user's own items
        seller_param = self.request.query_params.get('seller')
        if seller_param == 'me' and self.request.user.is_authenticated:
            return Item.objects.filter(seller=self.request.user)

        # Public seller page support: /items/?seller=<username>
        if seller_param and seller_param != 'me':
            qs = Item.objects.filter(seller__username=seller_param)
            # Only the owner can see unavailable items.
            if not (
                self.request.user.is_authenticated
                and self.request.user.username == seller_param
            ):
                qs = qs.filter(is_available=True)
            return qs
        # Use model method for everything else
        return Item.search_items(
            query=self.request.query_params.get('search'),
            category=self.request.query_params.get('category'),
            min_price=self.request.query_params.get('min_price'),
            max_price=self.request.query_params.get('max_price'),
            condition=self.request.query_params.get('condition'),
            is_on_sale=self.request.query_params.get('is_on_sale'),
            min_rating=self.request.query_params.get('min_rating')
        )

    @action(detail=True, methods=['get'])
    def suggestions(self, request, pk=None):
        """GET /items/{id}/suggestions/ - Get recommendations, related, seller's other items, and best sellers in category"""
        item = self.get_object()

        # Other items in the same category (excluding current item)
        related = Item.objects.filter(
            item_category=item.item_category
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
        best_sellers_key = item.get_item_category_display()
        if item.item_category == 'other' and item.custom_category:
            best_sellers_key = item.custom_category.title()

        best_sellers = best_sellers_by_category.get(best_sellers_key, [])
        best_sellers = [i for i in best_sellers if i.id != item.id]
    
        return Response({
            'related': ItemListSerializer(related, many=True, context={'request': request}).data,
            'seller_items': ItemListSerializer(seller_items, many=True, context={'request': request}).data,
            'best_sellers_in_category': ItemListSerializer(best_sellers, many=True, context={'request': request}).data,
        })

# ==================== REVIEW ENDPOINTS ====================

class ReviewView(ModelViewSet):
    queryset = Review.objects.select_related('item', 'reviewer', 'order').all()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ReviewCreateUpdateSerializer
        return ReviewSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action in ['update', 'partial_update', 'destroy']:
            if not self.request.user.is_authenticated:
                return qs.none()
            return qs.filter(reviewer=self.request.user)
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item_id = serializer.validated_data.get('item_id')
        order_id = serializer.validated_data.get('order_id')
        if not item_id:
            return Response({'item_id': ['This field is required.']}, status=status.HTTP_400_BAD_REQUEST)
        if not order_id:
            return Response({'order_id': ['This field is required.']}, status=status.HTTP_400_BAD_REQUEST)

        item = get_object_or_404(Item, id=item_id)
        order = get_object_or_404(Order, id=order_id)

        review = serializer.save(
            reviewer=request.user,
            item=item,
            order=order,
        )

        read_serializer = ReviewSerializer(review, context={'request': request})
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def upvote(self, request, pk=None):
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)
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