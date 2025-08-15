from .models import Profile
from django.contrib.auth.models import User
from rest_framework import serializers

class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

# Base class for profile 
class BuyerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    buyer_orders = serializers.SerializerMethodField()
    
    class Meta: 
        model = Profile
        fields = [
            'username', 'image', 'bio', 'created_at', 'phone_number', 
            'address', 'city', 'postal_code', 'total_sales', 'is_seller',
            'buyer_orders',
        ]
    
    def get_buyer_orders(self, obj):
        # All orders placed by this user as a buyer
        return [order.id for order in obj.user.orders.all()]

class SellerSerializer(BuyerSerializer):
    seller_orders = serializers.SerializerMethodField()

    class Meta(BuyerSerializer.Meta):
        fields = BuyerSerializer.Meta.fields + [
            'seller_rating', 'total_sales', 'marketing_emails', 'seller_orders'
        ]

    def get_seller_orders(self, obj):
        # All orders where this user is the seller
        # Find all OrderItems where item.seller == obj.user, then get their orders
        from orders.models import OrderItem
        order_ids = OrderItem.objects.filter(item__seller=obj.user).values_list('order_id', flat=True).distinct()
        return list(order_ids)

class ProfileCreateUpdate(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            'image', 'bio', 'phone_number',
            'address', 'city', 'postal_code', 'country',
            'marketing_emails', 'is_seller'
        ]