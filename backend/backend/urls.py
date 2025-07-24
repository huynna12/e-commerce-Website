from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import settings
from users.views import RegisterView
from items.views import HomepageView
from django.conf.urls.static import static

urlpatterns = [
    path('homepage/', HomepageView.as_view(), name='homepage'),
    path('admin/', admin.site.urls),
    path('', include('items.urls')),   # No /api prefix
    path('profile/', include('users.urls')),   # No /api prefix
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='get_token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh_token'),
    path('api-auth/', include('rest_framework.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
  
