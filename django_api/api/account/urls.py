
from django.urls import path, include
from .views import CustomTokenObtainPairView, UserViewSet
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework import routers

router = routers.DefaultRouter()
router.register("users", UserViewSet, basename="users")

urlpatterns = [
    path('', include(router.urls)),
    path('token/', CustomTokenObtainPairView.as_view(), name='token-obtain'),
    path('token-refresh/', TokenRefreshView.as_view(), name='token-refresh')
]