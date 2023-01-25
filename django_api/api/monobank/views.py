
from .serializers import CategorySerializer
from .models import Category
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.viewsets import ModelViewSet


class CategoryViewSet(ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    http_method_names = ['get']

    def get_permissions(self):
        permission = IsAdminUser()
        if self.action in ('retrieve', 'list'):
            permission = IsAuthenticated()

        return [permission]
