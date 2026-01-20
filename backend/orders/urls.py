from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import OrderViewSet, CartView, CartItemsView, CartItemDetailView, CheckoutView

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
	path('', include(router.urls)),
	path('cart/', CartView.as_view(), name='cart'),
	path('cart/items/', CartItemsView.as_view(), name='cart-items'),
	path('cart/items/<int:item_id>/', CartItemDetailView.as_view(), name='cart-item-detail'),
	path('checkout/', CheckoutView.as_view(), name='checkout'),
]
