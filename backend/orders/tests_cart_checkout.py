from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from items.models import Item
from orders.models import Cart, Order, OrderItem


class CartCheckoutFlowTest(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.user = User.objects.create_user(username='buyer', email='buyer@example.com', password='pass')
		self.seller = User.objects.create_user(username='seller', email='seller@example.com', password='pass')

		self.item = Item.objects.create(
			item_name='Test Item',
			item_price=Decimal('50.00'),
			item_category='electronics',
			item_quantity=5,
			seller=self.seller,
		)

		self.client.force_authenticate(user=self.user)

	def test_add_to_cart_and_checkout_creates_order_and_reduces_stock(self):
		res = self.client.post('/api/cart/items/', {'item_id': self.item.id, 'quantity': 2}, format='json')
		self.assertEqual(res.status_code, 200)
		self.assertEqual(res.data['total_quantity'], 2)

		# Missing required shipping fields
		bad = self.client.post('/api/checkout/', {}, format='json')
		self.assertEqual(bad.status_code, 400)

		payload = {
			'shipping_address': '123 Main St',
			'shipping_city': 'City',
			'shipping_postal_code': '12345',
			'shipping_country': 'Country',
			'payment_method': 'mock',
		}
		ok = self.client.post('/api/checkout/', payload, format='json')
		self.assertEqual(ok.status_code, 201)

		order_id = ok.data['id']
		order = Order.objects.get(id=order_id)
		self.assertEqual(order.user, self.user)
		self.assertEqual(order.status, 'processing')
		self.assertEqual(order.total_price, Decimal('100.00'))

		order_items = list(OrderItem.objects.filter(order=order))
		self.assertEqual(len(order_items), 1)
		self.assertEqual(order_items[0].item_id, self.item.id)
		self.assertEqual(order_items[0].quantity, 2)
		self.assertEqual(order_items[0].price, Decimal('50.00'))

		self.item.refresh_from_db()
		self.assertEqual(self.item.item_quantity, 3)
		self.assertEqual(self.item.times_purchased, 2)

		# Cart emptied
		cart = Cart.objects.get(user=self.user)
		self.assertEqual(cart.items.count(), 0)

	def test_checkout_fails_if_not_enough_stock(self):
		self.client.post('/api/cart/items/', {'item_id': self.item.id, 'quantity': 10}, format='json')
		payload = {
			'shipping_address': '123 Main St',
			'shipping_city': 'City',
			'shipping_postal_code': '12345',
			'shipping_country': 'Country',
		}
		res = self.client.post('/api/checkout/', payload, format='json')
		self.assertEqual(res.status_code, 400)
		self.assertIn('Not enough stock', res.data['detail'])
