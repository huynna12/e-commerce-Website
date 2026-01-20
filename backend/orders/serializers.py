from rest_framework import serializers

from .models import Order, OrderItem, Cart, CartItem
from items.serializers import ItemImageSerializer
from django.conf import settings


class OrderItemSerializer(serializers.ModelSerializer):
	item_name = serializers.CharField(source='item.item_name', read_only=True)
	item_id = serializers.IntegerField(source='item.id', read_only=True)

	class Meta:
		model = OrderItem
		fields = ['item_id', 'item_name', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
	items = OrderItemSerializer(many=True, read_only=True)

	class Meta:
		model = Order
		fields = [
			'id', 'status', 'total_price',
			'created_at', 'updated_at',
			'items',
		]


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
