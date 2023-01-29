from .serializers import CategorySerializer, MonoAccountSerializer
from .models import Category, MonoAccount
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.viewsets import ModelViewSet


class CategoryViewSet(ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    http_method_names = ["get"]

    def get_permissions(self):
        permission = IsAuthenticated()
        return [permission]


class MonoAccountViewSet(ModelViewSet):
    serializer_class = MonoAccountSerializer
    queryset = MonoAccount.objects.all()
    http_method_names = ["get"]

    def get_permissions(self):
        permission = IsAdminUser()
        return [permission]
