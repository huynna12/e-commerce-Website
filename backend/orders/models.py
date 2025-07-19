from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone

'''
CONTENTS: 
├── Order Model
└── OrderItem Model
'''
class Order(models.Model):
    # Order status
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    # Fields
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    promos = models.ManyToManyField('items.Promotion', blank=True, related_name='promos')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing', db_index=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])

    # Shipping information
    shipping_address = models.TextField(default='Address to be provided')
    shipping_city = models.CharField(max_length=100, default='City to be provided')
    shipping_postal_code = models.CharField(max_length=20, default='00000')
    shipping_country = models.CharField(max_length=100, default='Country to be provided')
    
    # Order tracking
    tracking_number = models.CharField(max_length=100, blank=True)
    estimated_delivery = models.DateTimeField(null=True, blank=True)
    
    # Payment information
    payment_method = models.CharField(max_length=50, default='credit_card')
    payment_status = models.CharField(max_length=20, default='paid')
    
    # Additional fields
    notes = models.TextField(blank=True, help_text="Special instructions or notes")

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),            # User's orders by status
        ]

    def __str__(self):
        return f"Order #{self.id} by {self.user.username} - {self.status}"
    
    def apply_multiple_promos(self):
        # # Helper method to apply promo_type 'item' or 'seller' to the order_item
        def apply_item_promos(order_item, promos):
            price = order_item.price

            for promo in item_and_seller_promos:
                if promo.is_applicable_to_item(order_item):
                    price = promo.calculate_discount_amount(price)
            return price

        # Method starts here !! 
        # Filter promos by type efficiently
        item_and_seller_promos = self.promos.filter(promo_type__in=['item', 'seller'])
        checkout_promos = self.promos.filter(promo_type='checkout')

        # Apply item and seller promos to each order item
        subtotal = sum(
            apply_item_promos(order_item, item_and_seller_promos)
            for order_item in self.items.all()
        )

        # Apply checkout promos to the subtotal
        for promo in checkout_promos:
            if promo.is_valid():
                subtotal = promo.calculate_discount_amount(subtotal)

        return subtotal

class OrderItem(models.Model):
    # Fields
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey('items.Item', on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    
    price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Price at time of purchase"
    )
    
    # No duplicate item in the order
    class Meta:
        unique_together = ('order', 'item')

    def __str__(self):
        return f"x{self.quantity} {self.item.item_name} in Order #{self.order.id}"