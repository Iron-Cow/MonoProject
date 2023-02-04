from django.urls import path, include
from .views import CategoryViewSet, MonoAccountViewSet, MonoCardViewSet, MonoJarViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register("categories", CategoryViewSet, basename="categories")
router.register("monoaccounts", MonoAccountViewSet, basename="monoaccounts")
router.register("monocards", MonoCardViewSet, basename="monocards")
router.register("monojars", MonoJarViewSet, basename="monojars")

urlpatterns = [
    path("", include(router.urls)),
]
