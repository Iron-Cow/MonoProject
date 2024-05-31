import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from monobank.models import JarTransaction, MonoAccount, MonoJar
from monobank.views import MonoJarTransactionViewSet
from rest_framework.exceptions import ErrorDetail

from .conftest import Variant

User = get_user_model()


@pytest.mark.django_db
def test_create_jar_transaction_from_webhook(pre_created_mono_jar):
    user = User.objects.create_user("test_user", "test_password")

    monoJar = MonoJar.objects.get(id="pre_created_jar_id2")
    transaction_data = {
        "id": "FUTockmzmwvnuCL0",
        "time": 1665250419,
        "description": "Укрпошта",
        "mcc": 5999,
        "originalMcc": 5999,
        "amount": -18200,
        "operationAmount": -18200,
        "currencyCode": 980,
        "commissionRate": 0,
        "cashbackAmount": 0,
        "balance": 6961482,
        "hold": True,
    }

    # Call the task function directly
    JarTransaction.create_jar_transaction_from_webhook(  # type: ignore
        monoJar.id,  # Pass the account ID
        transaction_data,
    )

    # Retrieve the created transaction from the database
    try:
        mono_jar_transaction = JarTransaction.objects.get(id=transaction_data["id"])
        assert mono_jar_transaction.id == transaction_data["id"]
        assert mono_jar_transaction.time == transaction_data["time"]
        assert mono_jar_transaction.description == transaction_data["description"]
        # Add assertions for other fields
    except ObjectDoesNotExist:
        pytest.fail("Transaction was not created")


monojartransactions_variants = [
    (
        "monojartransactions retrieve admin",
        Variant(
            view=MonoJarTransactionViewSet.as_view({"get": "retrieve"}),
            name="monojartransactions-detail",
            is_admin=True,
            tg_id="admin_name",
            url_kwargs={"pk": "pre_created_id"},
            expected={
                "id": "pre_created_id",
                "amount": -5000,
                "account_id": "pre_created_jar_id",
                "currency": {"code": 980, "name": "UAH", "flag": "🇺🇦", "symbol": "грн"},
                "balance": 10000,
                "category": "precreated_category_name1",
                "category_symbol": "smbl",
                "description": "pre_created_description",
                "owner_name": "User-precreated_user_tg_id",
            },
        ),
    ),
    (
        "monojartransactions retrieve owner",
        Variant(
            view=MonoJarTransactionViewSet.as_view({"get": "retrieve"}),
            name="monojartransactions-detail",
            is_admin=False,
            tg_id="precreated_user_tg_id",
            url_kwargs={"pk": "pre_created_id"},
            expected={
                "id": "pre_created_id",
                "amount": -5000,
                "account_id": "pre_created_jar_id",
                "currency": {"code": 980, "name": "UAH", "flag": "🇺🇦", "symbol": "грн"},
                "balance": 10000,
                "category": "precreated_category_name1",
                "category_symbol": "smbl",
                "description": "pre_created_description",
                "owner_name": "User-precreated_user_tg_id",
            },
        ),
    ),
    (
        "monojartransactions retrieve not owner",
        Variant(
            view=MonoJarTransactionViewSet.as_view({"get": "retrieve"}),
            name="monojartransactions-detail",
            is_admin=False,
            tg_id="some_user",
            status_code=404,
            url_kwargs={"pk": "pre_created_id"},
            expected={"detail": ErrorDetail(string="Not found.", code="not_found")},
        ),
    ),
    (
        "monojartransactions list admin",
        Variant(
            view=MonoJarTransactionViewSet.as_view({"get": "list"}),
            name="monojartransactions-list",
            is_admin=True,
            tg_id="admin_name",
            expected=[
                {
                    "id": "pre_created_id",
                    "amount": -5000,
                    "account_id": "pre_created_jar_id",
                    "currency": {
                        "code": 980,
                        "name": "UAH",
                        "flag": "🇺🇦",
                        "symbol": "грн",
                    },
                    "balance": 10000,
                    "category": "precreated_category_name1",
                    "category_symbol": "smbl",
                    "description": "pre_created_description",
                    "owner_name": "User-precreated_user_tg_id",
                },
                {
                    "id": "pre_created_id2",
                    "amount": -15000,
                    "account_id": "pre_created_jar_id2",
                    "currency": {
                        "code": 980,
                        "name": "UAH",
                        "flag": "🇺🇦",
                        "symbol": "грн",
                    },
                    "balance": 10000,
                    "category": "precreated_category_name2",
                    "category_symbol": "smbl",
                    "description": "pre_created_description2",
                    "owner_name": "User-precreated_user_tg_id",
                },
                {
                    "id": "some_tr_id",
                    "amount": -15000,
                    "account_id": "some_id_for_jar_transactions",
                    "currency": {
                        "code": 980,
                        "name": "UAH",
                        "flag": "🇺🇦",
                        "symbol": "грн",
                    },
                    "balance": 10000,
                    "category": "precreated_category_name2",
                    "category_symbol": "smbl",
                    "description": "",
                    "owner_name": "User-any_id",
                },
            ],
        ),
    ),
    (
        "monojartransactions list admin with filter",
        Variant(
            view=MonoJarTransactionViewSet.as_view({"get": "list"}),
            name="monojartransactions-list",
            is_admin=True,
            tg_id="admin_name",
            request_data={"users": "precreated_user_tg_id"},
            expected=[
                {
                    "id": "pre_created_id",
                    "amount": -5000,
                    "account_id": "pre_created_jar_id",
                    "currency": {
                        "code": 980,
                        "name": "UAH",
                        "flag": "🇺🇦",
                        "symbol": "грн",
                    },
                    "balance": 10000,
                    "category": "precreated_category_name1",
                    "category_symbol": "smbl",
                    "description": "pre_created_description",
                    "owner_name": "User-precreated_user_tg_id",
                },
                {
                    "id": "pre_created_id2",
                    "amount": -15000,
                    "account_id": "pre_created_jar_id2",
                    "currency": {
                        "code": 980,
                        "name": "UAH",
                        "flag": "🇺🇦",
                        "symbol": "грн",
                    },
                    "balance": 10000,
                    "category": "precreated_category_name2",
                    "category_symbol": "smbl",
                    "description": "pre_created_description2",
                    "owner_name": "User-precreated_user_tg_id",
                },
            ],
        ),
    ),
    (
        "monojartransactions list owner",
        Variant(
            view=MonoJarTransactionViewSet.as_view({"get": "list"}),
            name="monojartransactions-list",
            is_admin=False,
            tg_id="precreated_user_tg_id",
            expected=[
                {
                    "id": "pre_created_id",
                    "amount": -5000,
                    "account_id": "pre_created_jar_id",
                    "currency": {
                        "code": 980,
                        "name": "UAH",
                        "flag": "🇺🇦",
                        "symbol": "грн",
                    },
                    "balance": 10000,
                    "category": "precreated_category_name1",
                    "category_symbol": "smbl",
                    "description": "pre_created_description",
                    "owner_name": "User-precreated_user_tg_id",
                },
                {
                    "id": "pre_created_id2",
                    "amount": -15000,
                    "account_id": "pre_created_jar_id2",
                    "currency": {
                        "code": 980,
                        "name": "UAH",
                        "flag": "🇺🇦",
                        "symbol": "грн",
                    },
                    "balance": 10000,
                    "category": "precreated_category_name2",
                    "category_symbol": "smbl",
                    "description": "pre_created_description2",
                    "owner_name": "User-precreated_user_tg_id",
                },
            ],
        ),
    ),
    (
        "monojartransactions list owner with jar filter",
        Variant(
            view=MonoJarTransactionViewSet.as_view({"get": "list"}),
            name="monojartransactions-list",
            is_admin=False,
            tg_id="precreated_user_tg_id",
            request_data={"jars": "pre_created_jar_id"},
            expected=[
                {
                    "id": "pre_created_id",
                    "amount": -5000,
                    "account_id": "pre_created_jar_id",
                    "currency": {
                        "code": 980,
                        "name": "UAH",
                        "flag": "🇺🇦",
                        "symbol": "грн",
                    },
                    "balance": 10000,
                    "category": "precreated_category_name1",
                    "category_symbol": "smbl",
                    "description": "pre_created_description",
                    "owner_name": "User-precreated_user_tg_id",
                },
            ],
        ),
    ),
    (
        "monojartransactions list owner with jar filter multiple jars",
        Variant(
            view=MonoJarTransactionViewSet.as_view({"get": "list"}),
            name="monojartransactions-list",
            is_admin=False,
            tg_id="precreated_user_tg_id",
            request_data={"jars": "pre_created_jar_id,pre_created_jar_id2"},
            expected=[
                {
                    "id": "pre_created_id",
                    "amount": -5000,
                    "account_id": "pre_created_jar_id",
                    "currency": {
                        "code": 980,
                        "name": "UAH",
                        "flag": "🇺🇦",
                        "symbol": "грн",
                    },
                    "balance": 10000,
                    "category": "precreated_category_name1",
                    "category_symbol": "smbl",
                    "description": "pre_created_description",
                    "owner_name": "User-precreated_user_tg_id",
                },
                {
                    "id": "pre_created_id2",
                    "amount": -15000,
                    "account_id": "pre_created_jar_id2",
                    "currency": {
                        "code": 980,
                        "name": "UAH",
                        "flag": "🇺🇦",
                        "symbol": "грн",
                    },
                    "balance": 10000,
                    "category": "precreated_category_name2",
                    "category_symbol": "smbl",
                    "description": "pre_created_description2",
                    "owner_name": "User-precreated_user_tg_id",
                },
            ],
        ),
    ),
]


@pytest.mark.django_db
@pytest.mark.parametrize("test_name, variant", monojartransactions_variants)
def test_monojartransactions(
    api_request,
    test_name,
    variant,
    pre_created_mono_jar_transaction,
    pre_created_currency,
    pre_created_categories_mso,
):
    user = User.objects.create_user(
        "any_id",
        variant.password,
    )

    account = MonoAccount.objects.create(
        user=user,
        mono_token="unique_token",
        active=True,
    )

    jar = MonoJar.objects.create(
        monoaccount=account,
        id="some_id_for_jar_transactions",
        send_id="some_id",
        title="pre_created_title",
        currency=pre_created_currency,
        balance=100,
        goal=333,
    )

    JarTransaction.objects.create(
        id="some_tr_id",
        time=12345,
        description="",
        mcc=pre_created_categories_mso[1],
        amount=-15000,
        commission_rate=0,
        currency=pre_created_currency,
        balance=10000,
        hold=True,
        account=jar,
        cashback_amount=0,
    )
    view = variant.view

    response = view(
        api_request(
            variant.name,
            tg_id=variant.tg_id,
            method_name=variant.method_name,
            is_admin=variant.is_admin,
            url_kwargs=variant.url_kwargs,
            data=variant.request_data,
            create_new_user=variant.create_new_user,
            url_args=(),
        ),
        **variant.url_kwargs,
    )
    # assert response.status_code == variant.status_code
    assert response.data == variant.expected
