from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
	OrderViewSet,
	CartView,
	CartItemsView,
	CartItemDetailView,
	CheckoutView,
	OrderShippingUpdateView,
	OrderCancelRequestView,
	OrderCancelItemsRequestView,
	SellerOrdersView,
	SellerOrderDetailView,
	SellerCancellationDecisionView,
	SellerCancelItemsView,
)

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
	path('', include(router.urls)),
	path('cart/', CartView.as_view(), name='cart'),
	path('cart/items/', CartItemsView.as_view(), name='cart-items'),
	path('cart/items/<int:item_id>/', CartItemDetailView.as_view(), name='cart-item-detail'),
	path('checkout/', CheckoutView.as_view(), name='checkout'),
	path('orders/<int:order_id>/shipping/', OrderShippingUpdateView.as_view(), name='order-shipping-update'),
	path('orders/<int:order_id>/cancel-request/', OrderCancelRequestView.as_view(), name='order-cancel-request'),
	path('orders/<int:order_id>/cancel-items/', OrderCancelItemsRequestView.as_view(), name='order-cancel-items'),
	path('seller/orders/', SellerOrdersView.as_view(), name='seller-orders'),
	path('seller/orders/<int:order_id>/', SellerOrderDetailView.as_view(), name='seller-order-detail'),
	path('seller/orders/<int:order_id>/cancel-decision/', SellerCancellationDecisionView.as_view(), name='seller-cancel-decision'),
	path('seller/orders/<int:order_id>/cancel-items/', SellerCancelItemsView.as_view(), name='seller-cancel-items'),
]
