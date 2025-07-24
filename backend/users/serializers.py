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

class BuyerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    # Only include public fields
    class Meta:
        model = Profile
        fields = [
            'username', 'image', 'bio', 'created_at'
        ]

class SellerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = Profile
        fields = [
            'username', 'image', 'bio', 'is_seller', 'seller_rating',
            'total_sales', 'created_at'
        ]

class ProfileCreateUpdate(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            'image', 'bio', 'phone_number',
            'address', 'city', 'postal_code', 'country',
            'marketing_emails', 'is_seller'
        ]