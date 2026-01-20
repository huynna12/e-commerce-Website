from django.contrib.auth.models import User
from .models import Profile
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import (
    ProfileCreateUpdate,
    PublicProfileSerializer,
    PrivateProfileSerializer,
    PrivateSellerProfileSerializer,
    RegisterSerializer
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
        username = self.kwargs['username']
        is_owner = self.request.user.is_authenticated and self.request.user.username == username

        if is_owner:
            return PrivateSellerProfileSerializer if profile.is_seller else PrivateProfileSerializer
        return PublicProfileSerializer

class ProfileCreateUpdateView(generics.UpdateAPIView):
    queryset = Profile.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileCreateUpdate

    def get_object(self):
        username = self.kwargs.get('username')
        if username and username != self.request.user.username:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only edit your own profile")
        return self.request.user.profile