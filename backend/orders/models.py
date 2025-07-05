from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone

class Order(models.Model):
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
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
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    estimated_delivery = models.DateTimeField(null=True, blank=True)
    
    # Payment information
    payment_method = models.CharField(max_length=50, default='credit_card')
    payment_status = models.CharField(max_length=20, default='paid')
    
    # Additional fields
    notes = models.TextField(blank=True, help_text="Special instructions or notes")

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['tracking_number']),
        ]

    def __str__(self):
        return f"Order #{self.id} by {self.user.username} - {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    item = models.ForeignKey('items.Item', on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Price at time of purchase"
    )
    
    class Meta:
        unique_together = ('order', 'item')
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['item']),
        ]

    def __str__(self):
        return f"{self.quantity}x {self.item.item_name} in Order #{self.order.id}"
    
    @property
    def total_price(self):
        """Total price for this line item"""
        return self.quantity * self.price