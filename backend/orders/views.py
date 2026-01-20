from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from items.models import Item
from .models import Order, OrderItem, Cart, CartItem
from .serializers import OrderSerializer, CartSerializer


class OrderViewSet(ReadOnlyModelViewSet):
	serializer_class = OrderSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		return (
			Order.objects
			.filter(user=self.request.user)
			.prefetch_related('items', 'items__item')
			.order_by('-created_at')
		)


def _get_or_create_cart(user):
	cart, _ = Cart.objects.get_or_create(user=user)
	return cart


class CartView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		cart = _get_or_create_cart(request.user)
		serializer = CartSerializer(cart, context={'request': request})
		return Response(serializer.data)

	def delete(self, request):
		cart = _get_or_create_cart(request.user)
		cart.items.all().delete()
		serializer = CartSerializer(cart, context={'request': request})
		return Response(serializer.data)


class CartItemsView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request):
		item_id = request.data.get('item_id')
		quantity = request.data.get('quantity', 1)
		try:
			item_id = int(item_id)
			quantity = int(quantity)
		except (TypeError, ValueError):
			return Response({'detail': 'Invalid item_id or quantity'}, status=status.HTTP_400_BAD_REQUEST)

		if quantity < 1:
			return Response({'detail': 'Quantity must be at least 1'}, status=status.HTTP_400_BAD_REQUEST)

		item = Item.objects.filter(id=item_id, is_available=True).first()
		if not item:
			return Response({'detail': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

		cart = _get_or_create_cart(request.user)
		cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item, defaults={'quantity': quantity})
		if not created:
			cart_item.quantity += quantity
			cart_item.save(update_fields=['quantity', 'updated_at'])

		serializer = CartSerializer(cart, context={'request': request})
		return Response(serializer.data, status=status.HTTP_200_OK)


class CartItemDetailView(APIView):
	permission_classes = [IsAuthenticated]

	def patch(self, request, item_id: int):
		quantity = request.data.get('quantity')
		try:
			quantity = int(quantity)
		except (TypeError, ValueError):
			return Response({'detail': 'Invalid quantity'}, status=status.HTTP_400_BAD_REQUEST)

		if quantity < 1:
			return Response({'detail': 'Quantity must be at least 1'}, status=status.HTTP_400_BAD_REQUEST)

		cart = _get_or_create_cart(request.user)
		cart_item = CartItem.objects.filter(cart=cart, item_id=item_id).select_related('item').first()
		if not cart_item:
			return Response({'detail': 'Item not in cart'}, status=status.HTTP_404_NOT_FOUND)

		cart_item.quantity = quantity
		cart_item.save(update_fields=['quantity', 'updated_at'])
		serializer = CartSerializer(cart, context={'request': request})
		return Response(serializer.data, status=status.HTTP_200_OK)

	def delete(self, request, item_id: int):
		cart = _get_or_create_cart(request.user)
		deleted, _ = CartItem.objects.filter(cart=cart, item_id=item_id).delete()
		if deleted == 0:
			return Response({'detail': 'Item not in cart'}, status=status.HTTP_404_NOT_FOUND)
		serializer = CartSerializer(cart, context={'request': request})
		return Response(serializer.data, status=status.HTTP_200_OK)


class CheckoutView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request):
		shipping_address = (request.data.get('shipping_address') or '').strip()
		shipping_city = (request.data.get('shipping_city') or '').strip()
		shipping_postal_code = (request.data.get('shipping_postal_code') or '').strip()
		shipping_country = (request.data.get('shipping_country') or '').strip()
		payment_method = (request.data.get('payment_method') or 'mock').strip()
		notes = (request.data.get('notes') or '').strip()

		required = {
			'shipping_address': shipping_address,
			'shipping_city': shipping_city,
			'shipping_postal_code': shipping_postal_code,
			'shipping_country': shipping_country,
		}
		missing = [k for k, v in required.items() if not v]
		if missing:
			return Response({'detail': f"Missing required fields: {', '.join(missing)}"}, status=status.HTTP_400_BAD_REQUEST)

		cart = _get_or_create_cart(request.user)
		cart_items = list(cart.items.select_related('item').all())
		if not cart_items:
			return Response({'detail': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

		with transaction.atomic():
			item_ids = [ci.item_id for ci in cart_items]
			locked_items = {
				i.id: i for i in Item.objects.select_for_update().filter(id__in=item_ids)
			}

			# Validate stock and availability
			total = Decimal('0.00')
			for ci in cart_items:
				item = locked_items.get(ci.item_id)
				if not item or not item.is_available:
					return Response({'detail': f"Item {ci.item_id} is not available"}, status=status.HTTP_400_BAD_REQUEST)
				if item.item_quantity < ci.quantity:
					return Response({'detail': f"Not enough stock for {item.item_name}"}, status=status.HTTP_400_BAD_REQUEST)
				unit_price = Decimal(str(item.current_price))
				total += unit_price * ci.quantity

			order = Order.objects.create(
				user=request.user,
				status='processing',
				total_price=total,
				shipping_address=shipping_address,
				shipping_city=shipping_city,
				shipping_postal_code=shipping_postal_code,
				shipping_country=shipping_country,
				payment_method=payment_method,
				payment_status='paid',
				notes=notes,
			)

			for ci in cart_items:
				item = locked_items[ci.item_id]
				unit_price = Decimal(str(item.current_price))
				OrderItem.objects.create(order=order, item=item, quantity=ci.quantity, price=unit_price)
				item.item_quantity -= ci.quantity
				item.times_purchased += ci.quantity
				if item.item_quantity <= 0:
					item.item_quantity = 0
					item.is_available = False
				item.save(update_fields=['item_quantity', 'times_purchased', 'is_available', 'updated_at'])

			cart.items.all().delete()

		serializer = OrderSerializer(order)
		return Response(serializer.data, status=status.HTTP_201_CREATED)
