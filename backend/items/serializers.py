from rest_framework import serializers
from .models import Item, Review, Promotion
from .models.item import ItemImage
from django.conf import settings

def _default_image_data(context):
    request = context.get('request') if context else None
    default_rel = settings.MEDIA_URL.rstrip('/') + '/item_images/default.png'
    default_url = request.build_absolute_uri(default_rel) if request else default_rel
    return {'id': None, 'image_file': default_url, 'image_url': ''}

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

class ReviewCreateUpdateSerializer(serializers.ModelSerializer):
    item_id = serializers.IntegerField(write_only=True, required=False)
    order_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    class Meta:
        model = Review
        fields = ['item_id', 'rating', 'content', 'order_id', 'media']

    def create(self, validated_data):
        validated_data.pop('item_id', None)
        validated_data.pop('order_id', None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('item_id', None)
        validated_data.pop('order_id', None)
        return super().update(instance, validated_data)

class ItemImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemImage
        fields = ['id', 'image_file', 'image_url']

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
            'display_category', 'is_on_sale',
            'is_in_stock', 'review_stats'
        ]

    def get_review_stats(self, obj):
        return Review.get_item_stats(obj)
    
    def get_item_image(self, obj):
        first_image = obj.item_images.first()
        if first_image:
            return ItemImageSerializer(first_image, context=self.context).data
        return _default_image_data(self.context)

class ItemDetailSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    item_images = serializers.SerializerMethodField()
    current_price = serializers.ReadOnlyField()
    display_category = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    is_in_stock = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    is_sale_active = serializers.ReadOnlyField()
    display_condition = serializers.ReadOnlyField()
    review_stats = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = [
            'id', 'item_name', 'item_summary', 'item_desc', 'item_price', 
            'current_price', 'item_quantity', 'item_images',
            'item_category', 'display_category', 'custom_category',
            'item_sku', 'item_origin', 'display_condition',
            'item_condition',
            'is_available', 'is_on_sale', 'is_digital', 'is_in_stock',
            'sale_price', 'sale_start_date', 'sale_end_date', 'is_sale_active',
            'discount_percentage',
            'seller_name', 'view_count', 'times_purchased',
            'review_count', 'created_at', 'updated_at',
            'reviews', 'review_stats'
        ]

    def get_review_stats(self, obj):
        return Review.get_item_stats(obj)
    
    def get_item_images(self, obj):
        images = list(obj.item_images.all())
        if images:
            return ItemImageSerializer(images, many=True, context=self.context).data
        return [_default_image_data(self.context)]

class ItemCreateUpdateSerializer(serializers.ModelSerializer):
    seller = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Item
        fields = [
            'item_name', 'item_summary', 'item_desc', 'item_price', 'item_quantity', 'item_category',
            'custom_category', 'item_origin', 'item_condition', 'is_available', 'is_on_sale',
            'is_digital', 'sale_price', 'sale_start_date', 'sale_end_date', 'item_sku', 'seller', 'id'
        ]

    def _set_images(self, item, images_data):
        item.item_images.all().delete()

        if images_data:
            for image_data in images_data:
                if not image_data:
                    continue
                file_val = image_data.get('image_file')
                url_val = image_data.get('image_url')
                if file_val:
                    ItemImage.objects.create(item=item, image_file=file_val)
                elif url_val and str(url_val).strip():
                    ItemImage.objects.create(item=item, image_url=str(url_val).strip())