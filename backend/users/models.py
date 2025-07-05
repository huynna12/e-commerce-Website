from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class Profile(models.Model):
    # Core relationship
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Profile information
    image = models.ImageField(default='profilepic.png', upload_to='profile_pictures')
    bio = models.TextField(max_length=500, blank=True, help_text="Tell us about yourself")
    
    # Contact information
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    
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
    email_notifications = models.BooleanField(default=True)
    marketing_emails = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['is_seller', 'seller_rating']),
        ]

    def __str__(self):
        return f"{self.user.username}'s profile"
    
    @property
    def full_address(self):
        """Get formatted full address"""
        parts = [self.address, self.city, self.postal_code, self.country]
        return ", ".join(part for part in parts if part)
    
    @property
    def is_verified_seller(self):
        """Check if seller is verified (has made sales)"""
        return self.is_seller and self.total_sales > 0
    
    def update_seller_stats(self):
        """Update seller rating and total sales"""
        if self.is_seller:
            from django.db.models import Avg, Count
            orders = self.user.items.aggregate(
                total_sales=Count('orderitem__order', distinct=True),
                avg_rating=Avg('reviews__rating')
            )
            
            self.total_sales = orders['total_sales'] or 0
            self.seller_rating = round(orders['avg_rating'] or 0.0, 2)
            self.save(update_fields=['total_sales', 'seller_rating'])