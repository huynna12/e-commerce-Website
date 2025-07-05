from rest_framework import serializers
from .models.item import Item
from .models.review import Review
from django.contrib.auth.models import User

# ==================== REVIEW SERIALIZERS ====================

class ReviewSerializer(serializers.ModelSerializer):
    """For displaying reviews"""
    reviewer_name = serializers.CharField(source='reviewer.username', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'reviewer_name', 'rating', 'comment', 
            'is_verified_purchase', 'helpful_count', 'created_at',
            'seller_response', 'response_date'
        ]

class ReviewCreateSerializer(serializers.ModelSerializer):
    """For creating new reviews"""
    class Meta:
        model = Review
        fields = ['item', 'rating', 'comment']
    
    def validate(self, data):
        """Check if user can review this item"""
        user = self.context['request'].user
        item = data['item']
        
        can_review, message = Review.can_user_review(user, item)
        if not can_review:
            raise serializers.ValidationError(message)
        
        return data
    
    def create(self, validated_data):
        """Auto-assign reviewer"""
        validated_data['reviewer'] = self.context['request'].user
        return super().create(validated_data)

# ==================== ITEM SERIALIZERS ====================

class ItemListSerializer(serializers.ModelSerializer):
    """Lightweight for homepage/search results"""
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    current_price = serializers.ReadOnlyField()  # Uses your @property
    display_category = serializers.ReadOnlyField()  # Uses your @property
    average_rating = serializers.ReadOnlyField()  # Uses your @property
    review_count = serializers.ReadOnlyField()  # Uses your @property
    is_in_stock = serializers.ReadOnlyField()  # Uses your @property
    
    class Meta:
        model = Item
        fields = [
            'id', 'item_name', 'item_summary', 'current_price', 'item_image',
            'display_category', 'item_condition', 'is_featured', 'is_on_sale',
            'seller_name', 'average_rating', 'review_count', 'is_in_stock'
        ]

class ItemDetailSerializer(serializers.ModelSerializer):
    """Full data for item detail pages"""
    reviews = ReviewSerializer(many=True, read_only=True)
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    
    # Use your model properties
    current_price = serializers.ReadOnlyField()
    display_category = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    is_in_stock = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    is_sale_active = serializers.ReadOnlyField()
    
    # Get review statistics
    review_stats = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = [
            # Basic info
            'id', 'item_name', 'item_summary', 'item_desc', 'item_price', 
            'current_price', 'item_quantity',
            
            # Images
            'item_image', 'item_images',
            
            # Category & details
            'item_category', 'display_category', 'custom_category',
            'item_sku', 'item_origin', 'item_condition', 'item_weight', 
            'item_dimensions', 'technical_specs',
            
            # Flags
            'is_featured', 'is_available', 'is_on_sale', 'is_digital', 'is_in_stock',
            
            # Sale info
            'sale_price', 'sale_start_date', 'sale_end_date', 'is_sale_active',
            'discount_percentage',
            
            # Seller & analytics
            'seller_name', 'view_count', 'times_purchased',
            'average_rating', 'review_count',
            
            # Timestamps
            'created_at', 'updated_at',
            
            # Related data
            'reviews', 'review_stats'
        ]
    
    def get_review_stats(self, obj):
        """Get comprehensive review statistics"""
        return Review.get_item_stats(obj)

class ItemCreateSerializer(serializers.ModelSerializer):
    """For creating/updating items"""
    class Meta:
        model = Item
        fields = [
            'item_name', 'item_summary', 'item_desc', 'item_price', 'item_quantity',
            'item_image', 'item_images', 'item_category', 'custom_category',
            'item_origin', 'item_condition', 'item_weight', 'item_dimensions',
            'technical_specs', 'is_featured', 'is_available', 'is_on_sale', 
            'is_digital', 'sale_price', 'sale_start_date', 'sale_end_date'
        ]
    
    def validate(self, data):
        """Custom validation"""
        # Require custom category when 'other' is selected
        if data.get('item_category') == 'other' and not data.get('custom_category'):
            raise serializers.ValidationError(
                "Custom category is required when 'Other' is selected"
            )
        
        # Sale price validation
        if data.get('is_on_sale') and data.get('sale_price'):
            if data['sale_price'] >= data.get('item_price', 0):
                raise serializers.ValidationError(
                    "Sale price must be lower than regular price"
                )
        
        return data
    
    def create(self, validated_data):
        """Auto-assign seller"""
        validated_data['seller'] = self.context['request'].user
        return super().create(validated_data)