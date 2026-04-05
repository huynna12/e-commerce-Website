from rest_framework import serializers

from .models import Order, OrderItem, Cart, CartItem, OrderCancellation, OrderItemCancellation
from items.serializers import ItemImageSerializer
from django.conf import settings


ITEM_ID_SOURCE = 'item.id'
ITEM_NAME_SOURCE = 'item.item_name'


class OrderItemSerializer(serializers.ModelSerializer):
	item_name = serializers.CharField(source=ITEM_NAME_SOURCE, read_only=True)
	item_id = serializers.IntegerField(source=ITEM_ID_SOURCE, read_only=True)
	seller_username = serializers.CharField(source='item.seller.username', read_only=True)
	cancellation_status = serializers.SerializerMethodField()

	class Meta:
		model = OrderItem 
		fields = ['item_id', 'item_name', 'seller_username', 'quantity', 'price', 'cancellation_status']

	def get_cancellation_status(self, obj):
		cr = getattr(obj, 'cancellation_request', None)
		return getattr(cr, 'status', None)


class OrderCancellationSerializer(serializers.ModelSerializer):
	seller_username = serializers.CharField(source='seller.username', read_only=True)
	decided_by_username = serializers.CharField(source='decided_by.username', read_only=True)

	class Meta:
		model = OrderCancellation
		fields = [
			'id',
			'seller_username',
			'status',
			'message',
			'requested_at',
			'decided_at',
			'decided_by_username',
		]


class OrderItemCancellationSerializer(serializers.ModelSerializer):
	order_item_id = serializers.IntegerField(source='order_item.id', read_only=True)
	item_id = serializers.IntegerField(source='order_item.item.id', read_only=True)
	item_name = serializers.CharField(source='order_item.item.item_name', read_only=True)
	seller_username = serializers.CharField(source='seller.username', read_only=True)
	decided_by_username = serializers.CharField(source='decided_by.username', read_only=True)
	quantity = serializers.IntegerField(source='order_item.quantity', read_only=True)
	price = serializers.DecimalField(source='order_item.price', max_digits=10, decimal_places=2, read_only=True)

	class Meta:
		model = OrderItemCancellation
		fields = [
			'id',
			'order_item_id',
			'item_id',
			'item_name',
			'seller_username',
			'status',
			'message',
			'requested_at',
			'decided_at',
			'decided_by_username',
			'quantity',
			'price',
		]


class OrderSerializer(serializers.ModelSerializer):
	items = OrderItemSerializer(many=True, read_only=True)
	# Legacy order-level cancellation (kept for backward compatibility)
	cancellation_requests = OrderCancellationSerializer(many=True, read_only=True)
	item_cancellation_requests = serializers.SerializerMethodField()
	refund_notice = serializers.SerializerMethodField()

	class Meta:
		model = Order
		fields = [
			'id', 'status', 'total_price',
			'created_at', 'updated_at',
			'items',
			'shipping_address', 'shipping_city', 'shipping_postal_code', 'shipping_country',
			'payment_method', 'payment_status',
			'notes',
			'refund_notice',
			'cancellation_requests',
			'item_cancellation_requests',
		]

	def get_item_cancellation_requests(self, obj):
		qs = (
			OrderItemCancellation.objects
			.filter(order_item__order=obj)
			.select_related('seller', 'decided_by', 'order_item', 'order_item__item')
			.order_by('-requested_at')
		)
		return OrderItemCancellationSerializer(qs, many=True, context=self.context).data

	def get_refund_notice(self, obj):
		# Payments are mocked in this project; we still surface clear UX messaging.
		if getattr(obj, 'payment_status', None) != 'paid':
			return None

		if obj.status in ('cancelled', 'refunded'):
			return 'Order cancelled. Refund will be issued shortly.'

		if getattr(obj, 'refund_pending', False):
			return 'Refund will be issued shortly for the cancelled item(s).'
		return None


class SellerOrderItemSerializer(serializers.ModelSerializer):
	item_id = serializers.IntegerField(source=ITEM_ID_SOURCE, read_only=True)
	item_name = serializers.CharField(source=ITEM_NAME_SOURCE, read_only=True)
	cancellation_status = serializers.SerializerMethodField()

	class Meta:
		model = OrderItem
		fields = ['item_id', 'item_name', 'quantity', 'price', 'cancellation_status']

	def get_cancellation_status(self, obj):
		cr = getattr(obj, 'cancellation_request', None)
		return getattr(cr, 'status', None)


class SellerOrderSerializer(serializers.ModelSerializer):
	buyer_username = serializers.CharField(source='user.username', read_only=True)
	items = serializers.SerializerMethodField()
	item_cancellation_requests = serializers.SerializerMethodField()

	class Meta:
		model = Order
		fields = [
			'id',
			'status',
			'total_price',
			'created_at',
			'buyer_username',
			'shipping_address', 'shipping_city', 'shipping_postal_code', 'shipping_country',
			'items',
			'item_cancellation_requests',
		]

	def get_items(self, obj):
		request = self.context.get('request')
		user = getattr(request, 'user', None)
		qs = obj.items.select_related('item').all()
		if user and user.is_authenticated:
			qs = qs.filter(item__seller=user)
		return SellerOrderItemSerializer(qs, many=True, context=self.context).data

	def get_item_cancellation_requests(self, obj):
		request = self.context.get('request')
		user = getattr(request, 'user', None)
		if not user or not user.is_authenticated:
			return []
		qs = (
			OrderItemCancellation.objects
			.filter(order_item__order=obj, seller=user)
			.select_related('seller', 'decided_by', 'order_item', 'order_item__item')
			.order_by('-requested_at')
		)
		return OrderItemCancellationSerializer(qs, many=True, context=self.context).data


def _default_image_data(context):
	request = context.get('request') if context else None
	default_rel = settings.MEDIA_URL.rstrip('/') + '/item_images/default.png'
	default_url = request.build_absolute_uri(default_rel) if request else default_rel
	return {'id': None, 'image_file': default_url, 'image_url': ''}


class CartItemSerializer(serializers.ModelSerializer):
	item_id = serializers.IntegerField(source='item.id', read_only=True)
	item_name = serializers.CharField(source='item.item_name', read_only=True)
	current_price = serializers.DecimalField(source='item.current_price', max_digits=10, decimal_places=2, read_only=True)
	item_image = serializers.SerializerMethodField()
	subtotal = serializers.SerializerMethodField()

	class Meta:
		model = CartItem
		fields = ['item_id', 'item_name', 'quantity', 'current_price', 'subtotal', 'item_image']

	def get_subtotal(self, obj):
		return str(obj.item.current_price * obj.quantity)

	def get_item_image(self, obj):
		first_image = obj.item.item_images.first()
		if first_image:
			return ItemImageSerializer(first_image, context=self.context).data
		return _default_image_data(self.context)


class CartSerializer(serializers.ModelSerializer):
	items = CartItemSerializer(many=True, read_only=True)
	total_quantity = serializers.IntegerField(read_only=True)
	total_price = serializers.SerializerMethodField()

	class Meta:
		model = Cart
		fields = ['items', 'total_quantity', 'total_price', 'updated_at']

	def get_total_price(self, obj):
		return str(obj.total_price)
