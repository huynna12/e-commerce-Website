# urls.py
from django.urls import path
from .views import ItemDetailView

urlpatterns = [
    path('<int:pk>/', ItemDetailView.as_view(), name='item-detail'),
]