from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

class Review(models.Model):

    # --- RELATIONSHIPS ---
    item = models.ForeignKey('Item', on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, null=True, blank=True, 
                             help_text="Order this review is associated with")  # NEW!
    
    # --- CORE FIELDS ---
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    comment = models.TextField(blank=True, help_text="Optional review comment")
    
    # --- FLAGS ---
    is_verified_purchase = models.BooleanField(
        default=False,
        help_text="Review from verified buyer"
    )
    helpful_count = models.PositiveIntegerField(
        default=0,
        help_text="How many users found this review helpful"
    )
    
    # --- SELLER RESPONSE ---
    seller_response = models.TextField(
        blank=True, 
        help_text="Seller's response to this review"
    )
    response_date = models.DateTimeField(
        null=True, blank=True,
        help_text="When seller responded"
    )
    
    # --- TIMESTAMPS ---
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('item', 'reviewer')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['item', 'rating']),
            models.Index(fields=['reviewer']),
            models.Index(fields=['item', '-helpful_count']),
            models.Index(fields=['order']),  # NEW!
        ]

    def __str__(self):
        return f"{self.reviewer.username} - {self.item.item_name} ({self.rating}/5)"
    
    def clean(self):
        """Custom validation"""
        # Prevent self-review (if item has a seller field)
        if hasattr(self.item, 'seller') and self.item.seller == self.reviewer:
            raise ValidationError("You cannot review your own item")
        
        # Ensure rating is within valid range
        if self.rating < 1 or self.rating > 5:
            raise ValidationError("Rating must be between 1 and 5")

    def save(self, *args, **kwargs):
        """Override save to auto-verify if from completed order"""
        if self.order and self.order.status == 'delivered':
            self.is_verified_purchase = True
        self.clean()
        super().save(*args, **kwargs)
    
    # --- INSTANCE METHODS ---
    def mark_helpful(self):
        """Increment helpful count"""
        self.helpful_count += 1
        self.save(update_fields=['helpful_count'])
    
    def add_seller_response(self, response, responding_user):
        """Add seller response to review"""
        if hasattr(self.item, 'seller') and responding_user == self.item.seller:
            self.seller_response = response
            self.response_date = timezone.now()
            self.save(update_fields=['seller_response', 'response_date'])
            return True
        return False
    
    # --- CLASS METHODS ---
    @classmethod
    def get_item_stats(cls, item):
        """Get comprehensive review statistics for an item"""
        from django.db.models import Avg, Count, Q
        
        reviews = cls.objects.filter(item=item)
        
        if not reviews.exists():
            return {
                'total_reviews': 0,
                'average_rating': 0,
                'verified_count': 0,
                'rating_distribution': {i: 0 for i in range(1, 6)},
                'percentage_recommend': 0
            }
        
        # Basic stats
        stats = reviews.aggregate(
            total_reviews=Count('id'),
            average_rating=Avg('rating'),
            verified_count=Count('id', filter=Q(is_verified_purchase=True)),
            four_plus_count=Count('id', filter=Q(rating__gte=4))
        )
        
        # Rating distribution
        distribution = reviews.values('rating').annotate(count=Count('rating'))
        rating_dist = {i: 0 for i in range(1, 6)}
        for entry in distribution:
            rating_dist[entry['rating']] = entry['count']
        
        # Recommendation percentage (4+ stars)
        total = stats['total_reviews']
        recommend_percentage = (stats['four_plus_count'] / total * 100) if total > 0 else 0
        
        return {
            'total_reviews': stats['total_reviews'],
            'average_rating': round(stats['average_rating'], 1) if stats['average_rating'] else 0,
            'verified_count': stats['verified_count'],
            'rating_distribution': rating_dist,
            'percentage_recommend': round(recommend_percentage, 1)
        }
    
    @classmethod
    def get_reviews_for_item(cls, item, rating=None, verified_only=False, most_helpful=False, limit=None):
        """Get filtered reviews for an item with various options"""
        reviews = cls.objects.filter(item=item).select_related('reviewer')
        
        # Apply filters
        if rating:
            reviews = reviews.filter(rating=rating)
        if verified_only:
            reviews = reviews.filter(is_verified_purchase=True)
        
        # Apply ordering
        if most_helpful:
            reviews = reviews.order_by('-helpful_count', '-created_at')
        else:
            reviews = reviews.order_by('-created_at')
        
        # Apply limit
        return reviews[:limit] if limit else reviews
    
    @classmethod
    def get_user_reviews(cls, user, limit=10):
        """Get reviews written by a user"""
        return cls.objects.filter(reviewer=user).select_related('item')[:limit]
    
    @classmethod
    def can_user_review(cls, user, item):
        """Simple review validation"""
        if not user.is_authenticated:
            return False, "Must be logged in"
        
        if cls.objects.filter(reviewer=user, item=item).exists():
            return False, "Already reviewed"
        
        # Simple check: Did user buy this item?
        from orders.models import OrderItem
        purchased = OrderItem.objects.filter(
            order__user=user,
            item=item,
            order__status='delivered'
        ).exists()
        
        if not purchased:
            return False, "Must purchase item first"
        
        return True, "Can review"