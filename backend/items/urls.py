from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HomepageView, ItemViewSet, ReviewView, MyReviewableItemsView
)

router = DefaultRouter()
router.register(r'items', ItemViewSet, basename='item')
router.register(r'reviews', ReviewView, basename='review')

urlpatterns = [
    # Item and Review endpoints (CRUD, listing, detail, custom actions)
    path('', include(router.urls)),
    # Dashboard/reviewable items
    path('my-reviewable-items/', MyReviewableItemsView.as_view(), name='my-reviewable-items'),
    # Homepage
    path('homepage/', HomepageView.as_view(), name='homepage'),
]