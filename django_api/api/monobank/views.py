from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.permissions import (
    AllowAny,
    BasePermission,
    IsAdminUser,
    IsAuthenticated,
)
from rest_framework.views import APIView, Response
from rest_framework.viewsets import ModelViewSet
from tests import mocks

from .models import Category, MonoAccount, MonoCard, MonoJar, MonoTransaction
from .serializers import (
    CategorySerializer,
    MonoAccountSerializer,
    MonoCardSerializer,
    MonoJarSerializer,
    MonoTransactionSerializer,
)

User = get_user_model()


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
    http_method_names = ["get", "post"]

    def get_permissions(self):
        permission = IsAdminUser()
        return [permission]


class MonoCardJarIsOwnerOrAdminPermission(BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return bool(request.user)

    def has_object_permission(self, request, view, obj):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return bool(
            request.user
            and obj.monoaccount.user.tg_id == request.user.tg_id
            or request.user.is_superuser
        )


class MonoCardViewSet(ModelViewSet):
    serializer_class = MonoCardSerializer
    http_method_names = ["get"]

    def get_permissions(self):
        permission = IsAdminUser()
        if self.action in ("list", "retrieve"):
            permission = MonoCardJarIsOwnerOrAdminPermission()
        return [permission]

    def get_queryset(self):
        users = self.request.query_params.get("users")
        if self.request.user.is_superuser:
            if users and self.action == "list":
                return MonoCard.objects.filter(
                    monoaccount__user__tg_id__in=users.split(",")
                )
            return MonoCard.objects.all()
        return MonoCard.objects.filter(monoaccount__user__tg_id=self.request.user.tg_id)


class MonoJarViewSet(ModelViewSet):
    serializer_class = MonoJarSerializer
    http_method_names = ["get"]

    def get_permissions(self):
        permission = IsAdminUser()
        if self.action in ("list", "retrieve"):
            permission = MonoCardJarIsOwnerOrAdminPermission()
        return [permission]

    def get_queryset(self):
        users = self.request.query_params.get("users")
        if self.request.user.is_superuser:
            if users and self.action == "list":
                return MonoJar.objects.filter(
                    monoaccount__user__tg_id__in=users.split(",")
                )
            return MonoJar.objects.all()
        return MonoJar.objects.filter(monoaccount__user__tg_id=self.request.user.tg_id)


class MonoTransactionViewSet(ModelViewSet):
    serializer_class = MonoTransactionSerializer
    http_method_names = ["get"]

    def get_permissions(self):
        permission = IsAuthenticated()
        # permission = AllowAny()
        # if self.action in ("list", "retrieve"): # TODO: fix it
        #     permission = MonoCardJarIsOwnerOrAdminPermission()
        return [permission]

    def get_queryset(self):
        # return MonoTransaction.objects.select_related('currency', 'account').all()
        users = self.request.query_params.get("users")
        if self.request.user.is_superuser:
            if users and self.action == "list":
                return MonoTransaction.objects.filter(
                    Q(
                        monocardtransaction__account__monoaccount__user__tg_id=self.request.user.tg_id
                    )
                    | Q(
                        monojartransaction__account__monoaccount__user__tg_id=self.request.user.tg_id
                    )
                )
            return MonoTransaction.objects.all()
        return MonoTransaction.objects.filter(
            Q(
                monocardtransaction__account__monoaccount__user__tg_id=self.request.user.tg_id
            )
            | Q(
                monojartransaction__account__monoaccount__user__tg_id=self.request.user.tg_id
            )
        )


class TestEndpoint(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        card = MonoCard.objects.get(id="g1cvdYvrSXbD7Z2Zqpl06w")
        print(card)
        card.get_transactions()
        query = MonoTransaction.objects.all()
        query = MonoTransaction.objects.filter(
            Q(account__id="uaITWuKphk9qXdbFY9LpLg")
            # |
            # Q(monojartransaction__account__monoaccount__user__tg_id=12345)
        )
        return Response(query.values())
