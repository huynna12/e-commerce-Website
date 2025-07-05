from django.urls import path
from . import views
from users.views import CreateUserView

urlpatterns = [
    path('register/', CreateUserView.as_view(), name='register'),

]