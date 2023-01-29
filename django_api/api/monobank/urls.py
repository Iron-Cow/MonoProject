from django.contrib import admin
from django.urls import path, include
from .views import CategoryViewSet, MonoAccountViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register("categories", CategoryViewSet, basename="categories")
router.register("monoaccounts", MonoAccountViewSet, basename="monoaccounts")

urlpatterns = [
    path("", include(router.urls)),
]
