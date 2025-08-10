from faker import Faker
from django.core.management.base import BaseCommand
from items.models import Item, Review
from items.models.item import ItemImage
from orders.models import Order, OrderItem
from django.contrib.auth.models import User
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Seed fake data with users, items, images, orders, and reviews'

    CATEGORY_CHOICES = [
        ('electronics', 'Electronics & Tech'),
        ('clothing', 'Clothing & Fashion'),
        ('home_kitchen', 'Home & Kitchen'),
        ('books_media', 'Books & Media'),
        ('sports_outdoors', 'Sports & Outdoors'),
        ('beauty_personal', 'Beauty & Personal Care'),
        ('toys_games', 'Toys & Games'),
        ('automotive', 'Automotive & Tools'),
        ('health_wellness', 'Health & Wellness'),
        ('jewelry_accessories', 'Jewelry & Accessories'),
        ('baby_kids', 'Baby & Kids'),
        ('pet_supplies', 'Pet Supplies'),
        ('office_supplies', 'Office & School Supplies'),
        ('collectibles', 'Collectibles & Art'),
        ('other', 'Other'),
    ]
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('used', 'Used'),
        ('refurbished', 'Refurbished'),
    ]

    def handle(self, *args, **kwargs):
        fake = Faker()
        sellers = self._create_users(fake, 10, prefix='seller')
        buyers = self._create_users(fake, 10, prefix='buyer')
        items = self._create_items(fake, sellers)
        orders = self._create_orders(fake, buyers, items)
        self._create_reviews(fake, orders)
        self.stdout.write(self.style.SUCCESS('Successfully seeded users, items, images, orders, and reviews!'))

    def _create_users(self, fake, count, prefix='user'):
        return [
            User.objects.create_user(username=f"{prefix}_{fake.unique.user_name()}")
            for _ in range(count)
        ]

    def _create_items(self, fake, sellers):
        items = []
        num = 0
        for _ in range(50):
            category = random.choice(self.CATEGORY_CHOICES)[0]
            condition = random.choice(self.CONDITION_CHOICES)[0]
            seller = random.choice(sellers)
            custom_category = ""
            if category == 'other':
                custom_category = "New category " + str(num)
                num += 1

            item = Item.objects.create(
                item_name=fake.word().title(),
                item_summary=fake.sentence(),
                item_desc=fake.text(max_nb_chars=150),
                item_price=Decimal(str(round(random.uniform(10, 500), 2))),
                item_quantity=random.randint(1, 30),
                item_category=category,
                custom_category=custom_category,
                item_condition=condition,
                seller=seller,
            )
            ItemImage.objects.create(item=item)
            items.append(item)
        return items

    def _create_orders(self, fake, buyers, items):
        orders = []
        for _ in range(20):
            user = random.choice(buyers)
            status = random.choice(['processing', 'shipped', 'delivered'])
            order = Order.objects.create(
                user=user,
                status=status,
                total_price=Decimal('0.00'),
                shipping_address=fake.address(),
                shipping_city=fake.city(),
                shipping_postal_code=fake.postcode(),
                shipping_country=fake.country(),
                payment_method='credit_card',
                payment_status='paid',
            )
            total = self._add_order_items(order, items)
            order.total_price = total
            order.save()
            orders.append(order)
        return orders

    def _add_order_items(self, order, items):
        total = Decimal('0.00')
        order_items = random.sample(items, k=random.randint(1, 4))
        for item in order_items:
            quantity = random.randint(1, 2)
            price = item.item_price
            OrderItem.objects.create(
                order=order,
                item=item,
                quantity=quantity,
                price=price,
            )
            total += price * quantity
        return total

    def _create_reviews(self, fake, orders):
        for order in orders:
            if order.status != 'delivered':
                continue
            for order_item in order.items.all():
                # This check is now redundant, but keep for safety:
                if order.user == order_item.item.seller:
                    continue
                if not Review.objects.filter(order=order, item=order_item.item, reviewer=order.user).exists():
                    Review.objects.create(
                        item=order_item.item,
                        reviewer=order.user,
                        order=order,
                        rating=random.randint(1, 5),
                        content=fake.sentence(),
                        is_verified_purchase=True
                    )