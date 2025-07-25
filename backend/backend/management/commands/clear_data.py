from django.core.management.base import BaseCommand
from items.models import Item, Review
from items.models.item import ItemImage
from orders.models import Order, OrderItem
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Clear all data from users, items, images, orders, and reviews (except superusers)'

    def handle(self, *args, **kwargs):
        Review.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        ItemImage.objects.all().delete()
        Item.objects.all().delete()
        self.stdout.write('Clearing everything except *superuser*')
        User.objects.exclude(is_superuser=True).delete()
        self.stdout.write(self.style.SUCCESS('Database cleared!'))