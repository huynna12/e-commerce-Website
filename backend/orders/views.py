from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from items.models import Item
from .models import Order, OrderItem, Cart, CartItem, OrderCancellation, OrderItemCancellation
from .serializers import OrderSerializer, CartSerializer, SellerOrderSerializer


class OrderViewSet(ReadOnlyModelViewSet):
	serializer_class = OrderSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		return (
			Order.objects
			.filter(user=self.request.user)
			.prefetch_related(
				'items',
				'items__item',
				'items__cancellation_request',
				'cancellation_requests',
				'cancellation_requests__seller',
				'cancellation_requests__decided_by',
			)
			.order_by('-created_at')
		)


def _order_is_editable(order: Order) -> bool:
	return order.status == 'processing'


def _parse_optional_item_ids(value):
	if value is None or value == [] or value == '':
		return None
	if not isinstance(value, list):
		raise ValueError('item_ids must be a list.')
	try:
		return [int(x) for x in value]
	except (TypeError, ValueError) as e:
		raise ValueError('item_ids must contain integers.') from e


def _seller_cancel_items_for_order(*, request, order: Order, item_ids, reason: str):
	qs = (
		OrderItem.objects
		.filter(order=order, item__seller=request.user)
		.select_related('item')
	)
	if item_ids:
		qs = qs.filter(item_id__in=item_ids)
	order_items = list(qs)
	if not order_items:
		return Response({'detail': 'No matching seller items found to cancel.'}, status=status.HTTP_400_BAD_REQUEST)

	with transaction.atomic():
		for oi in order_items:
			cr, created = OrderItemCancellation.objects.get_or_create(
				order_item=oi,
				defaults={
					'seller': request.user,
					'status': 'approved',
					'message': reason,
					'decided_at': timezone.now(),
					'decided_by': request.user,
				},
			)
			if not created:
				cr.status = 'approved'
				cr.decided_at = timezone.now()
				cr.decided_by = request.user
				if reason:
					if cr.message:
						cr.message = f"{cr.message}\nSeller cancellation: {reason}"
					else:
						cr.message = reason
				cr.save(update_fields=['status', 'decided_at', 'decided_by', 'message'])

			locked_oi = (
				OrderItem.objects
				.select_for_update()
				.select_related('item')
				.filter(id=oi.id)
				.first()
			)
			if locked_oi:
				_approve_item_cancellation(locked_oi)

	order = Order.objects.filter(id=order.id).prefetch_related('items', 'items__item', 'items__cancellation_request').get()
	refund_notice = 'If you collected payment, make sure to refund the buyer for the cancelled items.'
	return Response({'order': SellerOrderSerializer(order, context={'request': request}).data, 'refund_notice': refund_notice})


class OrderShippingUpdateView(APIView):
	permission_classes = [IsAuthenticated]

	def patch(self, request, order_id: int):
		order = get_object_or_404(Order, id=order_id, user=request.user)
		if not _order_is_editable(order):
			return Response({'detail': 'Order can no longer be edited.'}, status=status.HTTP_400_BAD_REQUEST)

		allowed_fields = {
			'shipping_address',
			'shipping_city',
			'shipping_postal_code',
			'shipping_country',
			'notes',
		}
		update_fields = []
		for field in allowed_fields:
			if field in request.data:
				val = (request.data.get(field) or '').strip() if isinstance(request.data.get(field), str) else request.data.get(field)
				if field.startswith('shipping_') and not val:
					return Response({'detail': f'{field} cannot be empty.'}, status=status.HTTP_400_BAD_REQUEST)
				setattr(order, field, val)
				update_fields.append(field)

		if not update_fields:
			return Response({'detail': 'No editable fields provided.'}, status=status.HTTP_400_BAD_REQUEST)

		order.save(update_fields=update_fields + ['updated_at'])
		return Response(OrderSerializer(order, context={'request': request}).data)


class OrderCancelRequestView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request, order_id: int):
		"""Backward compatible endpoint.

		If no items are provided, it requests cancellation for ALL items in the order.
		Preferred endpoint is OrderCancelItemsRequestView.
		"""
		order = get_object_or_404(Order.objects.prefetch_related('items'), id=order_id, user=request.user)
		item_ids = request.data.get('item_ids')
		if item_ids is None:
			item_ids = request.data.get('items')
		if not item_ids:
			item_ids = [oi.item_id for oi in order.items.all()]
		message = (request.data.get('message') or '').strip()
		return _handle_cancel_items_request(request, order_id=order_id, item_ids=item_ids, message=message)


def _handle_cancel_items_request(request, order_id: int, item_ids, message: str):
	order = get_object_or_404(Order, id=order_id, user=request.user)
	if order.status in ('cancelled', 'refunded'):
		return Response({'detail': 'Order is already cancelled/refunded.'}, status=status.HTTP_400_BAD_REQUEST)
	if not _order_is_editable(order):
		return Response({'detail': 'Order can no longer be cancelled.'}, status=status.HTTP_400_BAD_REQUEST)

	if not isinstance(item_ids, list) or not item_ids:
		return Response({'detail': 'item_ids must be a non-empty list.'}, status=status.HTTP_400_BAD_REQUEST)
	try:
		item_ids = [int(x) for x in item_ids]
	except (TypeError, ValueError):
		return Response({'detail': 'item_ids must contain integers.'}, status=status.HTTP_400_BAD_REQUEST)

	order_items = list(
		OrderItem.objects
		.filter(order=order, item_id__in=item_ids)
		.select_related('item', 'item__seller')
	)
	if not order_items:
		return Response({'detail': 'No matching items found in this order.'}, status=status.HTTP_400_BAD_REQUEST)

	with transaction.atomic():
		for oi in order_items:
			cr, created = OrderItemCancellation.objects.get_or_create(
				order_item=oi,
				defaults={'seller': oi.item.seller, 'status': 'pending', 'message': message},
			)
			if not created and cr.status == 'pending':
				cr.message = message
				cr.save(update_fields=['message'])

	order = Order.objects.filter(id=order.id).prefetch_related(
		'items', 'items__item', 'items__item__seller', 'items__cancellation_request',
	).get()
	return Response(OrderSerializer(order, context={'request': request}).data, status=status.HTTP_200_OK)


class OrderCancelItemsRequestView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request, order_id: int):
		item_ids = request.data.get('item_ids')
		if item_ids is None:
			item_ids = request.data.get('items')
		message = (request.data.get('message') or '').strip()
		return _handle_cancel_items_request(request, order_id=order_id, item_ids=item_ids, message=message)



def _recompute_order_total(order: Order) -> Decimal:
	items = list(OrderItem.objects.filter(order=order).values_list('quantity', 'price'))
	return sum((Decimal(str(price)) * int(qty) for qty, price in items), Decimal('0.00'))


def _approve_item_cancellation(order_item: OrderItem) -> None:
	"""Approve cancellation: restock and remove order item; update order total/status."""
	order = Order.objects.select_for_update().get(id=order_item.order_id)
	item = Item.objects.select_for_update().get(id=order_item.item_id)

	item.item_quantity += order_item.quantity
	if item.item_quantity > 0:
		item.is_available = True
	item.save(update_fields=['item_quantity', 'is_available', 'updated_at'])

	order_item.delete()

	new_total = _recompute_order_total(order)
	order.total_price = new_total
	order.refund_pending = True
	if new_total <= Decimal('0.00') or not OrderItem.objects.filter(order=order).exists():
		order.status = 'cancelled'
	order.save(update_fields=['total_price', 'status', 'refund_pending', 'updated_at'])


class SellerOrdersView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		qs = (
			Order.objects
			.filter(items__item__seller=request.user)
			.select_related('user')
			.prefetch_related('items', 'items__item', 'items__cancellation_request')
			.distinct()
			.order_by('-created_at')
		)
		serializer = SellerOrderSerializer(qs, many=True, context={'request': request})
		return Response(serializer.data)


class SellerOrderDetailView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request, order_id: int):
		order = (
			Order.objects
			.filter(id=order_id, items__item__seller=request.user)
			.select_related('user')
			.prefetch_related('items', 'items__item', 'items__cancellation_request')
			.distinct()
			.first()
		)
		if not order:
			return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
		return Response(SellerOrderSerializer(order, context={'request': request}).data)


class SellerCancellationDecisionView(APIView):
	permission_classes = [IsAuthenticated]

	def patch(self, request, order_id: int):
		decision = (request.data.get('decision') or '').strip().lower()
		cancel_request_id = request.data.get('cancel_request_id')
		if decision not in ('approve', 'deny'):
			return Response({'detail': "decision must be 'approve' or 'deny'."}, status=status.HTTP_400_BAD_REQUEST)
		if cancel_request_id is None:
			return Response({'detail': 'cancel_request_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
		try:
			cancel_request_id = int(cancel_request_id)
		except (TypeError, ValueError):
			return Response({'detail': 'cancel_request_id must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)

		cr = (
			OrderItemCancellation.objects
			.select_related('order_item', 'order_item__order', 'order_item__item')
			.filter(id=cancel_request_id, seller=request.user, order_item__order_id=order_id)
			.first()
		)
		if not cr:
			return Response({'detail': 'Cancellation request not found.'}, status=status.HTTP_404_NOT_FOUND)
		if cr.status != 'pending':
			return Response({'detail': f'Cancellation already {cr.status}.'}, status=status.HTTP_400_BAD_REQUEST)
		order = cr.order_item.order
		if not _order_is_editable(order):
			return Response({'detail': 'Order can no longer be cancelled.'}, status=status.HTTP_400_BAD_REQUEST)

		with transaction.atomic():
			cr.status = 'approved' if decision == 'approve' else 'denied'
			cr.decided_at = timezone.now()
			cr.decided_by = request.user
			cr.save(update_fields=['status', 'decided_at', 'decided_by'])

			if cr.status == 'approved':
				# Remove item from the order and restock.
				_order_item = OrderItem.objects.select_for_update().filter(id=cr.order_item_id).select_related('item').first()
				if _order_item:
					_approve_item_cancellation(_order_item)

		order = Order.objects.filter(id=order_id).prefetch_related('items', 'items__item', 'items__cancellation_request').get()
		return Response(SellerOrderSerializer(order, context={'request': request}).data)


class SellerCancelItemsView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request, order_id: int):
		"""Seller-initiated cancellation for items they sold.

		Safe for multi-seller orders: a seller can only cancel their own order items.
		If this removes all remaining items in the order, the order becomes cancelled.
		"""
		order = (
			Order.objects
			.filter(id=order_id, items__item__seller=request.user)
			.distinct()
			.first()
		)
		if not order:
			return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
		if order.status in ('cancelled', 'refunded'):
			return Response({'detail': 'Order is already cancelled/refunded.'}, status=status.HTTP_400_BAD_REQUEST)
		if not _order_is_editable(order):
			return Response({'detail': 'Order can no longer be edited/cancelled.'}, status=status.HTTP_400_BAD_REQUEST)

		item_ids_raw = request.data.get('item_ids')
		if item_ids_raw is None:
			item_ids_raw = request.data.get('items')
		try:
			item_ids = _parse_optional_item_ids(item_ids_raw)
		except ValueError as e:
			return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

		reason = (request.data.get('message') or request.data.get('reason') or '').strip()
		if not reason:
			reason = 'Cancelled by seller.'

		return _seller_cancel_items_for_order(request=request, order=order, item_ids=item_ids, reason=reason)


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


class CheckoutError(Exception):
	def __init__(self, detail, status_code=status.HTTP_400_BAD_REQUEST):
		super().__init__(detail)
		self.detail = detail
		self.status_code = status_code


def _extract_checkout_payload(request):
	return {
		'shipping_address': (request.data.get('shipping_address') or '').strip(),
		'shipping_city': (request.data.get('shipping_city') or '').strip(),
		'shipping_postal_code': (request.data.get('shipping_postal_code') or '').strip(),
		'shipping_country': (request.data.get('shipping_country') or '').strip(),
		'payment_method': (request.data.get('payment_method') or 'mock').strip(),
		'notes': (request.data.get('notes') or '').strip(),
	}


def _validate_required_shipping_fields(payload):
	required_keys = [
		'shipping_address',
		'shipping_city',
		'shipping_postal_code',
		'shipping_country',
	]
	missing = [k for k in required_keys if not payload.get(k)]
	if missing:
		raise CheckoutError({'detail': f"Missing required fields: {', '.join(missing)}"})


def _get_cart_and_items(user):
	cart = _get_or_create_cart(user)
	cart_items = list(cart.items.select_related('item').all())
	if not cart_items:
		raise CheckoutError({'detail': 'Cart is empty'})
	return cart, cart_items


def _lock_items_for_cart_items(cart_items):
	item_ids = [ci.item_id for ci in cart_items]
	return {i.id: i for i in Item.objects.select_for_update().filter(id__in=item_ids)}


def _calculate_total_for_cart_items(cart_items, locked_items):
	total = Decimal('0.00')
	for ci in cart_items:
		item = locked_items.get(ci.item_id)
		if not item or not item.is_available:
			raise CheckoutError({'detail': f"Item {ci.item_id} is not available"})
		if item.item_quantity < ci.quantity:
			raise CheckoutError({'detail': f"Not enough stock for {item.item_name}"})
		unit_price = Decimal(str(item.current_price))
		total += unit_price * ci.quantity
	return total


def _create_order_from_payload(user, total, payload):
	return Order.objects.create(
		user=user,
		status='processing',
		total_price=total,
		shipping_address=payload['shipping_address'],
		shipping_city=payload['shipping_city'],
		shipping_postal_code=payload['shipping_postal_code'],
		shipping_country=payload['shipping_country'],
		payment_method=payload['payment_method'],
		payment_status='paid',
		notes=payload['notes'],
	)


def _create_order_items_and_update_stock(order, cart_items, locked_items):
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


class CheckoutView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request):
		payload = _extract_checkout_payload(request)
		try:
			_validate_required_shipping_fields(payload)
			cart, cart_items = _get_cart_and_items(request.user)
			with transaction.atomic():
				locked_items = _lock_items_for_cart_items(cart_items)
				total = _calculate_total_for_cart_items(cart_items, locked_items)
				order = _create_order_from_payload(request.user, total, payload)
				_create_order_items_and_update_stock(order, cart_items, locked_items)
				cart.items.all().delete()
		except CheckoutError as e:
			return Response(e.detail, status=e.status_code)

		serializer = OrderSerializer(order, context={'request': request})
		return Response(serializer.data, status=status.HTTP_201_CREATED)
