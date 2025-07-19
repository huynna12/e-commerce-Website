from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError
from orders.models import Order

class Promotion(models.Model):
    PROMO_TYPES = [
        ('item', 'Item Specific'),     
        ('checkout', 'Total Cost'),
        ('seller', 'Seller Specific'),
    ]
    
    promo_type = models.CharField(max_length=10, choices=PROMO_TYPES)
    sellers = models.ManyToManyField(User, blank=True, related_name='promo')
    items = models.ManyToManyField('Item', blank=True, related_name='promo')
    code = models.CharField(max_length=10, help_text='Promo code/ Coupon has to be less than 10 in length')
    discount_method = models.CharField(max_length=10, choices=[('percent', 'Percent'),('fixed', 'Fixed amount')])
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    description = models.TextField(blank=True, help_text='Optional description for this promotion')

    class Meta:
        ordering = ['-start_at']
        indexes = [
            models.Index(fields=['promo_type']),
        ]

    def __str__(self):
        return f'{self.get_promo_type_display()} - {self.code}'

    def is_valid(self):
        now = timezone.now()
        return (self.end_at >= now >= self.start_at)
    
    def clean(self):
        if self.start_at >= self.end_at:
            raise ValidationError('Invalid start or end time') 
        if self.discount_amount <= 0: 
            raise ValidationError('Input a possitive number')

    # Applies a list of promos sequentially to each order item in the order
    # Then to the order total if there is a 'checkout' promo
    # Return the final total after applying promos
    def is_applicable_to_item(self, order_item):
        if not self.is_valid():
            return False
        if order_item.item in self.items.all():
            return True
        if order_item.item.seller in self.sellers.all():
            return True
        return False

    def calculate_discounted_amount(self, amount):
        if self.discount_method == 'percent':
            return float(amount) * (1 - float(self.discount_amount) / 100)
        else:
            return max(float(amount) - float(self.discount_amount), 0)