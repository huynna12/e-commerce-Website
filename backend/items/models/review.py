from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Avg, Count, Q
# For checking media types
import mimetypes

class Review(models.Model):
    ''' FIELDS'''
    # Relationships
    item = models.ForeignKey('Item', on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_reviews')
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, null=True, blank=True)  # Optional, but required for verification  
    
    # Content
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    content = models.TextField(blank=True, help_text="Review's content")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Verified purchase, only verified buyers can review
    # Prevent fake reviews, seeding, etc.
    is_verified_purchase = models.BooleanField(
        default=False,
        help_text="Review from verified buyer (automatically set)"
    )

    # Upvotes
    helpful_count = models.IntegerField(default=0)
    upvoted_by = models.ManyToManyField(User, related_name='upvoted_reviews', blank=True)
    
    # Seller response to the review
    seller_response = models.TextField(
        blank=True, 
        help_text="Seller's response to this review"
    )
    response_date = models.DateTimeField(
        null=True, blank=True,
        help_text="When seller responded"
    )
    
    # Media attachment - optional
    media = models.FileField(
        upload_to='reviews/media/',
        blank=True,
        null=True,
        help_text="Optional image or video attachment (max 100MB)" 
    )

    ''' META '''
    class Meta:
        unique_together = ('order', 'item')  # One review per purchase
        ordering = ['-created_at']

        indexes = [
            models.Index(fields=['item', 'rating']),            # Reviews for this item with this rating
            models.Index(fields=['reviewer']),                  # Reviews by this user
            models.Index(fields=['item', '-helpful_count']),    # Reviews for this item sorted by helpfulness
            models.Index(fields=['order']),                     # Reviews associated with this order
        ]

    ''' INSTANCE METHODS '''
    def __str__(self):
        return f"{self.reviewer.username} - {self.item.item_name} ({self.rating}/5)"
    
    # Custom validation logic
    def clean(self):
        # Prevent self-review 
        if hasattr(self.item, 'seller') and self.item.seller == self.reviewer:
            raise ValidationError("You cannot review your own item")
        
        # Ensure rating is within valid range
        if self.rating < 1 or self.rating > 5:
            raise ValidationError("Rating must be between 1 and 5")
        
        # Must have a delivered order to review
        if not self.order:
            raise ValidationError("Review must be linked to an order")
        
        # Verify order belongs to reviewer
        if self.order.user != self.reviewer:
            raise ValidationError("Order does not belong to you")
        
        if not self.order.items.filter(item_id=self.item.id).exists():
            raise ValidationError("This item was not purchased in the specified order")
        
        # Order must be delivered/completed to review
        if self.order.status not in ['delivered', 'completed']:
            raise ValidationError("Can only review after order is delivered")
        
        if self.media: 
            mime_type, _ = mimetypes.guess_type(self.media.name)
            if not mime_type or not mime_type.startswith(('image', 'video')):
                raise ValidationError("Only image or video files are allowed")
    
        # Media file less than 100MB 
        if self.media and self.media.size > 100 * 1024 * 1024:  # 100MB limit
            raise ValidationError("File too large. Maximum size is 100MB.")

    # Auto-verify if review is from completed order
    def save(self, *args, **kwargs):
        # Set verification status based on purchase history
        if self.order and self.order.status in ['delivered', 'completed']:
            self.is_verified_purchase = True
        
        self.full_clean()  # This calls clean() and validates everything
        super().save(*args, **kwargs)

    # Increment helpful count
    def mark_helpful(self):
        self.helpful_count += 1
        self.save(update_fields=['helpful_count'])
    
    # Add seller response to review
    def add_seller_response(self, response_content, responder):
        # Check if the responder is the seller then save the response
        if hasattr(self.item, 'seller') and responder == self.item.seller:
            self.seller_response = response_content
            self.response_date = timezone.now()
            self.save(update_fields=['seller_response', 'response_date'])
            return True
        return False
    
    ''' CLASS METHODS '''
    # Get the stats for item reviews for display on item page
    @classmethod
    def get_item_stats(cls, item):
        reviews = cls.objects.filter(item=item)
        
        # Return None of no reviews exist
        if not reviews.exists():
            return None 
        
        # Basic stats
        stats = reviews.aggregate(
            total_reviews=Count('id'),
            average_rating=Avg('rating'),
            four_plus_count=Count('id', filter=Q(rating__gte=4))
        )
        
        # Rating distribution
        distribution = reviews.values('rating').annotate(count=Count('rating'))
        rating_dist = {str(i): 0 for i in range(5, 0, -1)}
        for entry in distribution:
            rating_dist[str(entry['rating'])] = entry['count']
        
        # Calculations
        total = stats['total_reviews']
        recommend_percentage = (stats['four_plus_count'] / total * 100) if total > 0 else 0
        media_count = reviews.filter(media__isnull=False).count()
        
        return {
            'total_reviews': stats['total_reviews'],  
            'average_rating': round(stats['average_rating'], 1) if stats['average_rating'] else 0,
            'rating_distribution': rating_dist,
            'percentage_recommend': round(recommend_percentage, 1),
            'reviews_with_media': media_count,
        }
    
    # Get reviews with media uploaded, limit for display purposes
    @classmethod
    def get_reviews_with_media(cls, item, limit=None):
        reviews = cls.objects.filter(
            item=item
        ).exclude(
            Q(media='') | Q(media__isnull=True)
        ).select_related('reviewer').order_by('-created_at')
        
        return reviews[:limit] if limit else reviews

