from django.contrib.auth.models import User
from .models import Profile
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import (
    ProfileCreateUpdate, BuyerSerializer, 
    SellerSerializer, RegisterSerializer
)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny] 

class ProfileDetailView(generics.RetrieveAPIView):
    queryset = Profile.objects.all()
    permission_classes = [AllowAny]  # Change to AllowAny to make profiles public
    lookup_field = 'user__username'
    
    def get_object(self):
        username = self.kwargs['username']
        return Profile.objects.get(user__username=username)
    
    def get_serializer_class(self):
        profile = self.get_object()
        if profile.is_seller:
            return SellerSerializer  # Should only expose public seller info in SellerSerializer
        return BuyerSerializer      # Should only expose public buyer info in BuyerSerializer

class ProfileCreateUpdateView(generics.UpdateAPIView):
    queryset = Profile.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileCreateUpdate

    def get_object(self):
        return self.request.user.profile