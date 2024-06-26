from django.contrib.auth import get_user_model
from django.db.models import Q
from pydantic import ValidationError
from rest_framework.permissions import (
    AllowAny,
    BasePermission,
    IsAdminUser,
    IsAuthenticated,
)
from rest_framework.views import APIView, Response
from rest_framework.viewsets import ModelViewSet

from .models import (
    Category,
    JarTransaction,
    MonoAccount,
    MonoCard,
    MonoDataNotFound,
    MonoJar,
    MonoTransaction,
)
from .pydantic import TransactionData
from .serializers import (
    CategorySerializer,
    MonoAccountSerializer,
    MonoCardSerializer,
    MonoJarSerializer,
    MonoJarTransactionSerializer,
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
        return MonoCard.objects.filter(
            Q(monoaccount__user__tg_id=self.request.user.tg_id)
            | Q(
                monoaccount__user__tg_id__in=[
                    member.tg_id for member in self.request.user.family_members.all()
                ]
            )
        )


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
        return MonoJar.objects.filter(
            Q(monoaccount__user__tg_id=self.request.user.tg_id)
            | Q(
                monoaccount__user__tg_id__in=[
                    member.tg_id for member in self.request.user.family_members.all()
                ]
            )
        )


class MonoTransactionIsOwnerOrAdminPermission(BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return bool(request.user)

    def has_object_permission(self, request, view, obj: MonoTransaction):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return bool(
            request.user
            and obj.account.monoaccount.user.tg_id == request.user.tg_id
            or request.user.is_superuser
        )


class MonoJarTransactionViewSet(ModelViewSet):
    serializer_class = MonoJarTransactionSerializer
    http_method_names = ["get"]

    def get_permissions(self):
        permission = IsAdminUser()
        if self.action in ("list", "retrieve"):  # TODO: fix it
            permission = MonoTransactionIsOwnerOrAdminPermission()
        return [permission]

    def get_queryset(self):

        users = self.request.query_params.get("users")
        jar_ids = self.request.query_params.get("jars")

        # all jar transactions from all users
        queryset = JarTransaction.objects.select_related("mcc", "account").order_by(
            "time", "id"
        )

        # filter by jar_id
        if jar_ids:
            queryset = queryset.filter(account_id__in=jar_ids.split(","))

        if self.request.user.is_superuser:
            if users and self.action == "list":
                queryset = queryset.filter(
                    account__monoaccount__user__tg_id__in=users.split(",")
                )
        else:
            queryset = queryset.filter(
                Q(account__monoaccount__user__tg_id=self.request.user.tg_id)
                | Q(
                    account__monoaccount__user__tg_id__in=[
                        member.tg_id
                        for member in self.request.user.family_members.all()
                    ]
                )
            )

        return queryset


class MonoTransactionViewSet(ModelViewSet):
    serializer_class = MonoTransactionSerializer
    http_method_names = ["get"]

    def get_permissions(self):
        permission = IsAdminUser()
        if self.action in ("list", "retrieve"):  # TODO: fix it
            permission = MonoTransactionIsOwnerOrAdminPermission()
        return [permission]

    def get_queryset(self):
        users = self.request.query_params.get("users")
        card_ids = self.request.query_params.get("cards")
        queryset = MonoTransaction.objects.select_related("mcc", "account").order_by(
            "time", "id"
        )

        # filter by card_id
        if card_ids:
            queryset = queryset.filter(account_id__in=card_ids.split(","))

        if self.request.user.is_superuser:
            if users and self.action == "list":
                queryset = queryset.filter(
                    account__monoaccount__user__tg_id__in=users.split(",")
                )
        else:
            queryset = queryset.filter(
                Q(account__monoaccount__user__tg_id=self.request.user.tg_id)
                | Q(
                    account__monoaccount__user__tg_id__in=[
                        member.tg_id
                        for member in self.request.user.family_members.all()
                    ]
                )
            )

        return queryset


class TransactionWebhookApiView(APIView):
    permission_classes = [AllowAny]
    http_method_names = ["post", "get"]

    def get(self, request):
        return Response(status=200)

    def _process_card_transaction(self, transaction_data: TransactionData):
        statement_item = transaction_data.statement_item
        transaction = MonoTransaction(
            account=transaction_data.account,
            id=statement_item.id,
            time=statement_item.time,
            description=statement_item.description,
            mcc=statement_item.mcc,
            original_mcc=statement_item.original_mcc,
            amount=statement_item.amount,
            operation_amount=statement_item.operation_amount,
            currency=statement_item.currency,
            commission_rate=statement_item.commission_rate,
            balance=statement_item.balance,
            hold=statement_item.hold,
            receipt_id=statement_item.receipt_id,
            cashback_amount=statement_item.cashback_amount,
            comment=statement_item.comment,
        )
        transaction.save()

    def _process_jar_transaction(self, transaction_data: TransactionData):
        statement_item = transaction_data.statement_item
        transaction = JarTransaction(
            account=transaction_data.account,
            id=statement_item.id,
            time=statement_item.time,
            description=statement_item.description,
            mcc=statement_item.mcc,
            original_mcc=statement_item.original_mcc,
            amount=statement_item.amount,
            operation_amount=statement_item.operation_amount,
            currency=statement_item.currency,
            commission_rate=statement_item.commission_rate,
            balance=statement_item.balance,
            hold=statement_item.hold,
            cashback_amount=statement_item.cashback_amount,
        )
        transaction.save()

    def post(self, request):
        user_key = request.query_params.get("token")
        if not user_key:
            return Response({"error": "token query param is not specified"}, status=403)

        try:
            parsed_data = TransactionData.parse_obj(request.data)
            if parsed_data.account.monoaccount.mono_token != user_key:
                return Response(
                    {"error": "invalid token or account missmatch"}, status=403
                )

            if isinstance(parsed_data.account, MonoCard):
                if MonoTransaction.objects.filter(
                    id=parsed_data.statement_item.id
                ).exists():
                    return Response(status=200)
                self._process_card_transaction(parsed_data)
            elif isinstance(parsed_data.account, MonoJar):
                if JarTransaction.objects.filter(
                    id=parsed_data.statement_item.id
                ).exists():
                    return Response(status=200)
                self._process_jar_transaction(parsed_data)

            return Response(status=201)
        except ValidationError:
            return Response({"error": f"Wrong request structure"}, status=422)

        except MonoDataNotFound as err:
            return Response({"error": f"Some data not found: {err}"}, status=404)


class TestEndpoint(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        account = User.objects.get(tg_id=11111)
        print(account)
        account.create_cards_jars()
        jar = MonoJar.objects.get(id="py6VpkfAYUx7w48jEU0F4EFqpkLw0to")
        print(jar)
        # jar.get_transactions()
        query = JarTransaction.objects.all()
        query = JarTransaction.objects.filter(
            Q(account__id="py6VpkfAYUx7w48jEU0F4EFqpkLw0to")
            # |
            # Q(monojartransaction__account__monoaccount__user__tg_id=12345)
        )
        return Response(query.values())
