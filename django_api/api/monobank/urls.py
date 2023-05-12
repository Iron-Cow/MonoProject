from django.urls import path, include
from .views import (
    CategoryViewSet,
    MonoAccountViewSet,
    MonoCardViewSet,
    MonoJarViewSet,
    MonoTransactionViewSet,
    TestEndpoint,
    )
from rest_framework import routers

router = routers.DefaultRouter()
router.register("categories", CategoryViewSet, basename="categories")
router.register("monoaccounts", MonoAccountViewSet, basename="monoaccounts")
router.register("monocards", MonoCardViewSet, basename="monocards")
router.register("monojars", MonoJarViewSet, basename="monojars")
router.register("monotransactions", MonoTransactionViewSet, basename="monotransactions")

urlpatterns = [
    path("", include(router.urls)),
    path("test/", TestEndpoint.as_view())
]
