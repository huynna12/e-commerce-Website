from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from items.models import Item


class ItemPermissionsApiTest(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.seller = User.objects.create_user(username='seller1', email='s1@example.com', password='pass')
		self.other = User.objects.create_user(username='buyer1', email='b1@example.com', password='pass')
		self.item = Item.objects.create(
			item_name='Seller Item',
			item_price=Decimal('10.00'),
			item_category='electronics',
			item_quantity=3,
			seller=self.seller,
		)

	def test_non_seller_cannot_update_item(self):
		self.client.force_authenticate(user=self.other)
		res = self.client.patch(f'/api/items/{self.item.id}/', {'item_name': 'Hacked'}, format='json')
		self.assertEqual(res.status_code, 403)

	def test_seller_can_update_item(self):
		self.client.force_authenticate(user=self.seller)
		res = self.client.patch(f'/api/items/{self.item.id}/', {'item_name': 'Updated'}, format='json')
		self.assertEqual(res.status_code, 200)
		self.item.refresh_from_db()
		self.assertEqual(self.item.item_name, 'Updated')
