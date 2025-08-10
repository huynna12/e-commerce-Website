from rest_framework import serializers
from .models import Item, Review, Promotion
from .models.item import ItemImage

'''
CONTENTS: 
├── Review Serializer
├── Review Create Serializer
├── Item List Serializer
├── Item Detail Serializer
├── Item Create Serializer
'''

# Serializers for Review model but not having item, since this is called 
# inside ItemDetailSerializer for ItemPage
class ReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.CharField(source='reviewer.username', read_only=True)
    is_upvoted = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            'id', 'reviewer', 'order', 'rating', 'content',
            'created_at','is_verified_purchase', 'helpful_count',
            'seller_response', 'response_date', 'media', 'is_upvoted', 
        ]

    def get_is_upvoted(self, obj):
        request = self.context.get('request', None)
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            return obj.upvoted_by.filter(id=user.id).exists()
        return False


# Creating and updating reviews (same fields for both operations)
class ReviewCreateUpdateSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = Review
        fields = ['rating', 'content', 'order_id', 'media']

class ItemImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemImage
        fields = ['id', 'image_file', 'image_url']

# Homepage and search results serializer
class ItemListSerializer(serializers.ModelSerializer):
    current_price = serializers.ReadOnlyField()  
    display_category = serializers.ReadOnlyField()  
    is_in_stock = serializers.ReadOnlyField()  
    item_image = serializers.SerializerMethodField()
    review_stats = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = [
            'id', 'item_name', 'current_price', 'item_image',
            'display_category', 'is_featured', 'is_on_sale',
            'is_in_stock', 'review_stats'
        ]

    def get_review_stats(self, obj):
        return Review.get_item_stats(obj)
    
    def get_item_image(self, obj):
        first_image = obj.item_images.first()
        if first_image:
            return ItemImageSerializer(first_image).data
        return None
    
# Full data for item page
class ItemDetailSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    item_images = ItemImageSerializer(many=True, read_only=True)

    # Use your model properties
    current_price = serializers.ReadOnlyField()
    display_category = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    is_in_stock = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    is_sale_active = serializers.ReadOnlyField()
    display_condition = serializers.ReadOnlyField()

    # Get review statistics
    review_stats = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = [
            # Basic info
            'id', 'item_name', 'item_summary', 'item_desc', 'item_price', 
            'current_price', 'item_quantity', 'item_images',
            
            # Category & details
            'display_category', 'custom_category',
            'item_sku', 'item_origin', 'display_condition', 'item_weight', 
            'item_dimensions', 'technical_specs',
            
            # Flags
            'is_featured', 'is_available', 'is_on_sale', 'is_digital', 'is_in_stock',
            
            # Sale info
            'sale_price', 'sale_start_date', 'sale_end_date', 'is_sale_active',
            'discount_percentage',
            
            # Seller & analytics
            'seller_name', 'view_count', 'times_purchased',
             'review_count',
            
            # Timestamps
            'created_at', 'updated_at',
            
            # Related data
            'reviews', 'review_stats'
        ]

    def get_review_stats(self, obj):
        return Review.get_item_stats(obj)

class ItemCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = [
            'item_name', 'item_summary', 'item_desc', 'item_price', 'item_quantity', 'item_category', 
            'custom_category', 'item_origin', 'item_condition', 'item_weight', 'item_dimensions',
            'technical_specs', 'is_featured', 'is_available', 'is_on_sale', 'is_digital', 'sale_price',
            'sale_start_date', 'sale_end_date'
        ]

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        item = Item.objects.create(**validated_data)
        for image_data in images_data:
            ItemImage.objects.create(item=item, **image_data)
        return item

    def update(self, instance, validated_data):
        images_data = validated_data.pop('images', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if images_data is not None:
            # Optionally clear existing images or update as needed
            instance.images.all().delete()
            for image_data in images_data:
                ItemImage.objects.create(item=instance, **image_data)
        return instance