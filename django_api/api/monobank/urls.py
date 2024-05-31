from django.urls import include, path
from rest_framework import routers

from .views import (
    CategoryViewSet,
    MonoAccountViewSet,
    MonoCardViewSet,
    MonoJarTransactionViewSet,
    MonoJarViewSet,
    MonoTransactionViewSet,
    TestEndpoint,
    TransactionWebhookApiView,
)

router = routers.DefaultRouter()
router.register("categories", CategoryViewSet, basename="categories")
router.register("monoaccounts", MonoAccountViewSet, basename="monoaccounts")
router.register("monocards", MonoCardViewSet, basename="monocards")
router.register("monojars", MonoJarViewSet, basename="monojars")
router.register("monotransactions", MonoTransactionViewSet, basename="monotransactions")
router.register(
    "monojartransactions", MonoJarTransactionViewSet, basename="monojartransactions"
)

urlpatterns = [
    path("", include(router.urls)),
    path("test/", TestEndpoint.as_view()),
    path("webhook/", TransactionWebhookApiView.as_view(), name="webhook"),
]
