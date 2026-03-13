from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from items.models import Item
from orders.models import Order, OrderItem, OrderItemCancellation


class OrderCancellationFlowTest(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.buyer = User.objects.create_user(username='buyer2', email='buyer2@example.com', password='pass')
		self.seller1 = User.objects.create_user(username='sellerA', email='sellerA@example.com', password='pass')
		self.seller2 = User.objects.create_user(username='sellerB', email='sellerB@example.com', password='pass')

		self.item1 = Item.objects.create(
			item_name='Item A',
			item_price=Decimal('10.00'),
			item_category='electronics',
			item_quantity=5,
			seller=self.seller1,
		)
		self.item2 = Item.objects.create(
			item_name='Item B',
			item_price=Decimal('20.00'),
			item_category='electronics',
			item_quantity=5,
			seller=self.seller2,
		)

	def _checkout_two_sellers(self):
		self.client.force_authenticate(user=self.buyer)
		self.client.post('/api/cart/items/', {'item_id': self.item1.id, 'quantity': 1}, format='json')
		self.client.post('/api/cart/items/', {'item_id': self.item2.id, 'quantity': 2}, format='json')
		payload = {
			'shipping_address': '123 Main St',
			'shipping_city': 'City',
			'shipping_postal_code': '12345',
			'shipping_country': 'Country',
			'payment_method': 'mock',
		}
		res = self.client.post('/api/checkout/', payload, format='json')
		self.assertEqual(res.status_code, 201)
		return res.data['id']

	def test_buyer_requests_cancel_and_sellers_must_all_approve(self):
		order_id = self._checkout_two_sellers()

		# Buyer requests cancellation for item1 only
		res = self.client.post(
			f'/api/orders/{order_id}/cancel-items/',
			{'item_ids': [self.item1.id], 'message': 'Please cancel item A'},
			format='json',
		)
		self.assertEqual(res.status_code, 200)
		self.assertEqual(OrderItemCancellation.objects.filter(order_item__order_id=order_id).count(), 1)
		cr = OrderItemCancellation.objects.get(order_item__order_id=order_id)
		self.assertEqual(cr.order_item.item_id, self.item1.id)

		# Seller1 approves; item is removed, order remains processing (because item2 still exists)
		self.client.force_authenticate(user=self.seller1)
		res2 = self.client.patch(
			f'/api/seller/orders/{order_id}/cancel-decision/',
			{'decision': 'approve', 'cancel_request_id': cr.id},
			format='json',
		)
		self.assertEqual(res2.status_code, 200)
		order = Order.objects.get(id=order_id)
		self.assertEqual(order.status, 'processing')

		# Buyer sees refund notice for approved cancellations
		self.client.force_authenticate(user=self.buyer)
		res3 = self.client.get(f'/api/orders/{order_id}/')
		self.assertEqual(res3.status_code, 200)
		self.assertIn('refund_notice', res3.data)
		self.assertTrue(res3.data['refund_notice'])

		# Item1 restocked, item2 remains reduced
		self.item1.refresh_from_db()
		self.item2.refresh_from_db()
		self.assertEqual(self.item1.item_quantity, 5)
		self.assertEqual(self.item2.item_quantity, 3)

	def test_buyer_can_update_shipping_while_processing(self):
		order_id = self._checkout_two_sellers()
		res = self.client.patch(
			f'/api/orders/{order_id}/shipping/',
			{'shipping_city': 'New City'},
			format='json',
		)
		self.assertEqual(res.status_code, 200)
		order = Order.objects.get(id=order_id)
		self.assertEqual(order.shipping_city, 'New City')

	def test_seller_can_cancel_their_items_and_total_updates(self):
		order_id = self._checkout_two_sellers()

		# Seller1 cancels only their own item (without a buyer request)
		self.client.force_authenticate(user=self.seller1)
		res = self.client.post(
			f'/api/seller/orders/{order_id}/cancel-items/',
			{'message': 'Out of stock - refund buyer'},
			format='json',
		)
		self.assertEqual(res.status_code, 200)
		self.assertIn('refund_notice', res.data)
		self.assertIn('order', res.data)

		# Item1 restocked; item2 remains reduced
		self.item1.refresh_from_db()
		self.item2.refresh_from_db()
		self.assertEqual(self.item1.item_quantity, 5)
		self.assertEqual(self.item2.item_quantity, 3)

		order = Order.objects.get(id=order_id)
		self.assertEqual(order.status, 'processing')
		# Remaining total should be item2(20) * 2 = 40
		self.assertEqual(order.total_price, Decimal('40.00'))

		remaining_items = list(OrderItem.objects.filter(order_id=order_id))
		self.assertEqual(len(remaining_items), 1)
		self.assertEqual(remaining_items[0].item_id, self.item2.id)
