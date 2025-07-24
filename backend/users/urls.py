from django.urls import path
from .views import ProfileDetailView, ProfileCreateUpdateView

urlpatterns = [
    path('<str:username>/', ProfileDetailView.as_view(), name='profile-detail'),
    path('<str:username>/edit/', ProfileCreateUpdateView.as_view(), name='profile-edit'),
]