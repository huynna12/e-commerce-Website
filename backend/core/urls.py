from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.conf import settings
from django.conf.urls.static import static

from users.views import RegisterView
from items.views import HomepageView

urlpatterns = [
    path("admin/", admin.site.urls),

    # API
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="api-schema"), name="api-docs"),
    path("api/homepage/", HomepageView.as_view(), name="homepage"),
    path("api/", include("items.urls")),
    path("api/profile/", include("users.urls")),
    path("api/", include("orders.urls")),
    path("api/register/", RegisterView.as_view(), name="register"),
    path("api/token/", TokenObtainPairView.as_view(), name="get_token"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="refresh_token"),
    path("api-auth/", include("rest_framework.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)