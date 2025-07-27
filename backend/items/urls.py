# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HomepageView, ItemViewSet, ReviewView, MyReviewableItemsView
)

router = DefaultRouter()
router.register(r'items', ItemViewSet, basename='item')

urlpatterns = [
    # Item endpoints (CRUD, listing, detail, custom actions)
    path('', include(router.urls)),
    # Review endpoints (create/update/delete via ReviewView)
    # Later change to slug:item_slug
    path('<int:item_id>/reviews/', ReviewView.as_view(), name='item-reviews'),  # POST for create
    path('reviews/<int:review_id>/', ReviewView.as_view(), name='review-detail'),      # PUT/PATCH/DELETE for update/delete

    # Dashboard/reviewable items
    path('my-reviewable-items/', MyReviewableItemsView.as_view(), name='my-reviewable-items'),
]