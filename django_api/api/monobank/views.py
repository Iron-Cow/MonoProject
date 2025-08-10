# pyright: reportIncompatibleMethodOverride = false
# pyright: reportAttributeAccessIssue = false
# pyright: reportUnknownVariableType = false

import logging
import os

from account.models import User as CustomUser
from ai_agent.agent import get_jar_monthly_report_html
from django.contrib.auth import get_user_model
from django.db.models import Q

# from loguru import logger
from pydantic import ValidationError
from rest_framework.decorators import action
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

logger = logging.getLogger(__name__)
User: CustomUser = get_user_model()  # type: ignore


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

    def has_permission(
        self, request, view
    ):  # pyright: ignore[reportIncompatibleMethodOverride]
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return bool(request.user)

    def has_object_permission(
        self, request, view, obj
    ):  # pyright: ignore[reportIncompatibleMethodOverride]
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
        users = self.request.query_params.get(
            "users"
        )  # pyright: ignore[reportAttributeAccessIssue]
        if self.request.user.is_superuser:
            if users and self.action == "list":
                return MonoCard.objects.filter(
                    monoaccount__user__tg_id__in=users.split(",")
                )
            return MonoCard.objects.all()
        return MonoCard.objects.filter(
            Q(
                monoaccount__user__tg_id=self.request.user.tg_id
            )  # pyright: ignore[reportAttributeAccessIssue]
            | Q(
                monoaccount__user__tg_id__in=[
                    member.tg_id
                    for member in self.request.user.family_members.all()  # pyright: ignore[reportAttributeAccessIssue]
                ]
            )
        )


class MonoJarViewSet(ModelViewSet):
    serializer_class = MonoJarSerializer
    http_method_names = ["get", "patch"]  # Added patch to support the new action

    def get_permissions(self):
        permission = IsAdminUser()
        if self.action in ("list", "retrieve", "set_budget_status"):
            permission = MonoCardJarIsOwnerOrAdminPermission()
        return [permission]

    def get_queryset(self):
        users = self.request.query_params.get("users")
        is_budget = self.request.query_params.get("is_budget")
        queryset = MonoJar.objects.all()

        # Filter by users if provided
        if self.request.user.is_superuser:
            if users and self.action == "list":
                queryset = queryset.filter(
                    monoaccount__user__tg_id__in=users.split(",")
                )
        else:
            queryset = queryset.filter(
                Q(
                    monoaccount__user__tg_id=self.request.user.tg_id
                )  # pyright: ignore[reportAttributeAccessIssue]
                | Q(
                    monoaccount__user__tg_id__in=[
                        member.tg_id
                        for member in self.request.user.family_members.all()  # pyright: ignore[reportAttributeAccessIssue]
                    ]
                )
            )

        # Filter by is_budget if provided
        if is_budget is not None:
            # Accept '1', 'true', 'True' as True, else False
            is_budget_bool = str(is_budget).lower() in ("1", "true", "yes")
            queryset = queryset.filter(is_budget=is_budget_bool)

        return queryset

    @action(detail=True, methods=["patch"])
    def set_budget_status(self, request, pk=None):
        """Set the budget status of a jar.

        Expects a boolean 'is_budget' in the request data.
        """
        jar = self.get_object()
        is_budget = request.data.get("is_budget")

        if is_budget is None:
            return Response({"error": "is_budget parameter is required"}, status=400)

        # Convert to boolean
        is_budget_bool = str(is_budget).lower() in ("1", "true", "yes")
        jar.is_budget = is_budget_bool
        jar.save()

        serializer = self.get_serializer(jar)
        return Response(serializer.data)


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
            logger.warning("token query param is not specified")
            return Response({"error": "token query param is not specified"}, status=403)

        try:
            parsed_data = TransactionData.parse_obj(request.data)
            if parsed_data.account.monoaccount.mono_token != user_key:
                logger.error(
                    f"invalid token or account missmatch: {user_key} for account {parsed_data.account}"
                )

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
        except ValidationError as err:
            logger.critical(err)
            return Response({"error": f"Wrong request structure"}, status=422)

        except MonoDataNotFound as err:
            logger.error(err)
            return Response({"error": f"Some data not found: {err}"}, status=404)


class TestEndpoint(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        logger.info("something went wrong")
        # from ai_agent.agent import get_monthly_jar_transactions_tool
        # get_monthly_jar_transactions_tool("2025-04-10")
        # return
        # result = agent.invoke(
        #     "Check monotranactions spends around 2025-04-10 and monojars transactions for same period. "
        #     "Transtactotions from card should be compensated from jar or by transfer from someone else. "
        #     "Please locate card transactions which were not covered this month."
        #     "Note, that jar name and transaction description may be different. As well as sum (it may wary by 5%).")
        result = get_jar_monthly_report_html("2025-07-10")
        import json

        from telegram.client import TelegramClient

        tg = TelegramClient(os.environ.get("BOT_TOKEN", "not set bot token"))
        tg.send_html_message(
            os.environ.get("ADMIN_TG_ID", "not set tg_id"), result.get("output", "{}")
        )

        return Response(
            {
                "input": result.get("input"),
                "output": result.get("output", "{}"),
            }
        )
        # bar_result = bar.delay()
        # result = bar_result.get()
        # account = User.objects.get(tg_id=11111)
        # print(account)
        # account.create_cards_jars()
        # jar = MonoJar.objects.get(id="py6VpkfAYUx7w48jEU0F4EFqpkLw0to")
        # print(jar)
        # # jar.get_transactions()
        # query = JarTransaction.objects.all()
        # query = JarTransaction.objects.filter(
        #     Q(account__id="py6VpkfAYUx7w48jEU0F4EFqpkLw0to")
        #     # |
        #     # Q(monojartransaction__account__monoaccount__user__tg_id=12345)
        # )
        return Response("")
        # )
        return Response("")
        # )
        return Response("")
