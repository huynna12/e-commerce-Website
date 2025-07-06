from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models import Q, Count, Avg
import uuid

class Item(models.Model):
    
    # --- CHOICES ---
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
    
    # --- BASIC FIELDS ---
    item_name = models.CharField(max_length=100, db_index=True)
    item_summary = models.CharField(
    max_length=200, 
    default="Product summary",
    help_text="Short summary for listings and search results"
    )
    item_desc = models.TextField(
        max_length=2000, 
        default="Product description",
        help_text="Detailed product description"
    )
    technical_specs = models.JSONField(
        default=dict, 
        blank=True, 
        help_text="Technical specifications as key-value pairs"
    )
    
    item_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    item_quantity = models.PositiveIntegerField(default=0)

    # --- IMAGE FIELDS ---
    item_image = models.ImageField(upload_to='item_images/', default='item_images/default.png')
    item_images = models.JSONField(default=list, blank=True, help_text="Additional image URLs")
    
    # --- CATEGORY FIELDS ---
    item_category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other', db_index=True)
    custom_category = models.CharField(max_length=100, blank=True, help_text="Custom category when 'Other' selected")
    
    # --- PRODUCT DETAILS ---
    item_sku = models.CharField(max_length=50, unique=True, blank=True)
    item_origin = models.CharField(max_length=100, default='Unknown')
    item_condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='new')
    item_weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Weight in kg")
    item_dimensions = models.JSONField(default=dict, blank=True, help_text="Dimensions as {length, width, height} in cm")
    
    # --- FLAGS ---
    is_featured = models.BooleanField(default=False, db_index=True)
    is_available = models.BooleanField(default=True, db_index=True)
    is_on_sale = models.BooleanField(default=False, db_index=True)
    is_digital = models.BooleanField(default=False, help_text="Digital product (no shipping required)")
    
    # --- RELATIONSHIPS ---
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items')
    
    # --- SALE FIELDS ---
    sale_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0.01)],
        help_text="Sale price (must be lower than regular price)"
    )
    sale_start_date = models.DateTimeField(null=True, blank=True)
    sale_end_date = models.DateTimeField(null=True, blank=True)

    # --- ANALYTICS FIELDS ---
    view_count = models.PositiveIntegerField(default=0)
    times_purchased = models.PositiveIntegerField(default=0)

    # --- TIMESTAMPS ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # --- ORDERING AND INDEXES ---
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['item_category', 'is_available']),
            models.Index(fields=['custom_category', 'is_available']),
            models.Index(fields=['seller', 'is_available']),
            models.Index(fields=['is_featured', 'is_available']),
            models.Index(fields=['is_on_sale', 'is_available']),
            models.Index(fields=['item_price']),
            models.Index(fields=['view_count']),
            models.Index(fields=['times_purchased']),
        ]
    
    # --- CORE METHODS ---
    def save(self, *args, **kwargs):
        # If category is 'other', require custom_category
        if self.item_category == 'other' and not self.custom_category:
            raise ValidationError("Custom category required when 'Other' selected")
        
        # Clean custom category
        if self.custom_category:
            self.custom_category = self.custom_category.strip().lower()
        
        # Generate SKU if not provided
        if not self.item_sku:
            self.item_sku = self.generate_sku()
        
        # Validate before saving
        self.full_clean()
        super().save(*args, **kwargs)
    
    def clean(self):
        # Sale price validation
        if self.is_on_sale:
            if not self.sale_price:
                raise ValidationError("Sale price required when on sale")
            if self.sale_price >= self.item_price:
                raise ValidationError("Sale price must be lower than regular price")
        
        # Date validation
        if self.sale_start_date and self.sale_end_date:
            if self.sale_start_date >= self.sale_end_date:
                raise ValidationError("Sale start date must be before end date")
    
    def __str__(self):
        return f"{self.item_name} - ({self.item_sku})"
    
    # --- ESSENTIAL PROPERTIES ---
    @property
    def display_category(self):
        """Display category name, or custom category if 'Other'"""
        if self.item_category == 'other' and self.custom_category:
            return self.custom_category.title()
        return self.get_item_category_display()
    
    @property
    def current_price(self):
        """Return the current price, checking for sale"""
        if self.is_sale_active and self.sale_price:
            return self.sale_price
        return self.item_price

    @property
    def is_sale_active(self):
        """Check the status of the sale"""
        if not self.is_on_sale or not self.sale_price:
            return False
        
        now = timezone.now()
        
        # Check if sale dates are set and valid
        if self.sale_start_date and now < self.sale_start_date:
            return False 
        if self.sale_end_date and now > self.sale_end_date:
            return False  
        
        return True
    
    @property
    def is_in_stock(self):
        """Check if the item is in stock"""
        return self.item_quantity > 0 and self.is_available
    
    @property
    def average_rating(self):
        """Get average rating from reviews"""
        reviews = self.reviews.all()
        if reviews.exists():
            return round(reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'], 1)
        return 0
    
    @property
    def review_count(self):
        """Get total number of reviews"""
        return self.reviews.count()
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage if on sale"""
        if self.is_sale_active and self.sale_price:
            return round(((self.item_price - self.sale_price) / self.item_price) * 100)
        return 0
    
    # --- STOCK MANAGEMENT ---
    def reduce_stock(self, amount):
        """Reduce stock for orders - thread-safe"""
        from django.db import transaction
        
        with transaction.atomic():
            # Re-fetch the item to ensure we have the latest stock count
            item = Item.objects.select_for_update().get(id=self.id)
            if item.item_quantity >= amount:
                item.item_quantity -= amount
                item.times_purchased += amount
                item.save(update_fields=['item_quantity', 'times_purchased'])
                return True
            return False
    
    def increment_view_count(self):
        """Increment view count atomically"""
        Item.objects.filter(id=self.id).update(view_count=models.F('view_count') + 1)
    
    # --- PRIVATE METHODS ---
    def generate_sku(self):
        """Generate unique SKU"""
        while True:
            if self.item_category == 'other' and self.custom_category:
                prefix = self.custom_category[:3].upper()
            else:
                prefix = self.item_category[:3].upper()
            
            # Generate a random part and combine with prefix
            random_part = str(uuid.uuid4()).replace('-', '')[:6].upper()
            sku = f"{prefix}{random_part}"
            
            # Only return if the SKU is unique
            if not Item.objects.filter(item_sku=sku).exists():
                return sku
    
    # --- CLASS METHODS ---
    @classmethod
    def search_items(cls, query=None, category=None, min_price=None, max_price=None, 
                    condition=None, is_on_sale=None, is_featured=None, min_rating=None):
        """Search items with multiple filters - optimized query"""
        items = cls.objects.select_related('seller').filter(is_available=True)

        # Text search filter
        if query:
            items = items.filter(
                Q(item_name__icontains=query) | 
                Q(item_summary__icontains=query) | 
                Q(item_description__icontains=query)
            )
        
        # Category filter
        if category:
            category = category.lower().strip()
            items = items.filter(Q(item_category=category) | Q(custom_category=category))
        
        # Price filters
        if min_price is not None:
            items = items.filter(item_price__gte=min_price)
        if max_price is not None:
            items = items.filter(item_price__lte=max_price)
        
        # Boolean filters
        if condition:
            items = items.filter(item_condition=condition)
        if is_on_sale is not None:
            items = items.filter(is_on_sale=is_on_sale)
        if is_featured is not None:
            items = items.filter(is_featured=is_featured)
        
        # Rating filter (requires subquery)
        if min_rating is not None:
            from django.db.models import Subquery, OuterRef
            rated_items = cls.objects.filter(
                id=OuterRef('id'),
                reviews__rating__gte=min_rating
            ).values('id')
            items = items.filter(id__in=Subquery(rated_items))
        
        return items.order_by('-is_featured', '-view_count', '-created_at')

    # --- CLASS METHODS FOR DISPLAYING ---
    @classmethod
    def get_all_categories(cls):
        """Get all available categories (standard + custom)"""
        standard = [choice[0] for choice in cls.CATEGORY_CHOICES if choice[0] != 'other']

        # Get custom categories from 'other' items
        custom = cls.objects.filter(
            item_category='other',
            custom_category__isnull=False,
            is_available=True
        ).values_list('custom_category', flat=True).distinct()
        
        return sorted(set(standard + list(custom)))
    
    @classmethod
    def get_trending_items(cls, limit=10):
        """Get trending items based on views and purchases"""
        return cls.objects.filter(
            is_available=True
        ).order_by('-view_count', '-times_purchased')[:limit]
    
    @classmethod
    def get_featured_items(cls, limit=10):
        """Get featured items"""
        return cls.objects.filter(
            is_featured=True,
            is_available=True
        ).order_by('-created_at')[:limit]
    
    @classmethod
    def get_best_sellers_by_category(cls, items_each_category, max_categories):
        """Get the best sellings items for each category"""
        categories = {}

        # Popular categories to display as default
        popular_categories = [
            'electronics', 'clothing', 'home_kitchen', 'beauty_personal',
            'sports_outdoors', 'office_supplies', 'health_wellness',
            'jewelry_accessories', 'toys_games', 'automotive',
        ][:max_categories]

        for cat in popular_categories:
            # Get the queryset of best selling items for the category 
            best_sellers = cls.objects.filter(
                item_category = cat, 
                is_available=True
            ).order_by('-times_purchased', '-view_count')[:items_each_category]

            # If there are best sellers, add them to the categories dictionary
            if best_sellers.exists():
                # Create a dummy to get the display name then use it as key
                # Convert the queryset to a list of items store it with the key
                dummy_item = cls(item_category=cat)
                display_name = dummy_item.get_item_category_display()
                categories[display_name] = list(best_sellers)

        return categories

    # --- USER TRACKING (Session-based) ---
    @classmethod
    def track_view(cls, item_id, request):
        """Track item view in session"""
        # If the viewed_items session doesn't exist, create it
        # Else, get the existing list
        viewed = request.session.get('viewed_items', [])
        
        # If the item_id is already in the list, remove the old it
        if item_id in viewed:
            viewed.remove(item_id)
        
        # Insert the item_id at the start of the list - behaving like a stack
        viewed.insert(0, item_id)
        request.session['viewed_items'] = viewed[:15]  # Keep last 15
        request.session.modified = True
    
    @classmethod
    def get_recently_viewed(cls, request, limit):
        """Get recently viewed items from session"""

        #  Get the list of viewed item_id from the session
        item_viewed = request.session.get('viewed_items', [])[:limit]
        
        # If no items are viewed, return empty queryset
        if not item_viewed:
            return cls.objects.none()
        
        # Create a dictionary of items for fast lookup
        # Go through all the items that are viewed and make their IDs the keys, values are the item objects
        items = {item.id: item for item in cls.objects.filter(
            id__in=item_viewed, is_available=True
        )}
        
        # Return the items in the order they were viewed
        return [items[item_id] for item_id in item_viewed if item_id in items]
    
    @classmethod
    def get_recommendations(cls, request, limit):
        """Get recommendations based on viewing history"""

        # Get recently viewed items
        recent = cls.get_recently_viewed(request, 3)
        
        # If no recent items, return trending items
        if not recent:
            return cls.get_trending_items(limit)
        
        # Get the categories and IDs of the recently viewed items
        categories = [item.item_category for item in recent]
        viewed_ids = [item.id for item in recent]
        
        # Filter items by categories, excluding recently viewed items
        return cls.objects.filter(
            item_category__in=categories,
            is_available=True
        ).exclude(id__in=viewed_ids).order_by('-times_purchased')[:limit]