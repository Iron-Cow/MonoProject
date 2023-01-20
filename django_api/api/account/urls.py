
from django.contrib import admin
from django.urls import path, include
from .views import UserView, CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("users/", UserView.as_view(), name='users'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token-obtain'),
    path('token-refresh/', TokenRefreshView.as_view(), name='token-refresh')
]