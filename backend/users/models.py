from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg, Count
from orders.models import OrderItem
   
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Profile information
    image = models.ImageField(default='profilepic.png', upload_to='profile_pictures')
    bio = models.TextField(max_length=500, blank=True, help_text="Tell us about yourself")
    
    # Contact information
    phone_number = models.CharField(max_length=17, blank=True)
    
    # Address information
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Seller information
    is_seller = models.BooleanField(default=False)
    seller_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_sales = models.PositiveIntegerField(default=0)
    
    # Preferences
    marketing_emails = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
    
    # Update seller stats based on actual orders
    # This method aggregates sales and ratings from OrderItem model
    def update_seller_stats(self):
        if self.is_seller:         
            stats = OrderItem.objects.filter(
                item__seller=self.user,
                order__status='delivered'  # Only count delivered orders
            ).aggregate(
                total_sales=Count('order', distinct=True),
                avg_rating=Avg('item__reviews__rating')
            )
            
            self.total_sales = stats['total_sales'] or 0
            self.seller_rating = round(stats['avg_rating'] or 0.0, 2)
            self.save(update_fields=['total_sales', 'seller_rating'])