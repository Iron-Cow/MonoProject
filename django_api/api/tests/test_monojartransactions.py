import time as _time

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
                "formatted_time": "1970-01-01 03:25:45",
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
                "formatted_time": "1970-01-01 03:25:45",
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
                    "formatted_time": "1970-01-01 03:25:45",
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
                    "formatted_time": "1970-01-01 03:25:45",
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
                    "formatted_time": "1970-01-01 03:25:45",
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
                    "formatted_time": "1970-01-01 03:25:45",
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
                    "formatted_time": "1970-01-01 03:25:45",
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
                    "formatted_time": "1970-01-01 03:25:45",
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
                    "formatted_time": "1970-01-01 03:25:45",
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
                    "formatted_time": "1970-01-01 03:25:45",
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
                    "formatted_time": "1970-01-01 03:25:45",
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
                    "formatted_time": "1970-01-01 03:25:45",
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


@pytest.mark.django_db
def test_monojartransactions_fields_selection(
    api_request,
    pre_created_mono_jar_transaction,
    pre_created_currency,
    pre_created_categories_mso,
):
    """Return only balance and formatted_time using fields query param."""
    User = get_user_model()
    user = User.objects.create_user("any_id_fs", "PassW0rd")
    account = MonoAccount.objects.create(
        user=user, mono_token="unique_token_fs", active=True
    )
    jar = MonoJar.objects.create(
        monoaccount=account,
        id="fields_test_jar_id",
        send_id="fields_test_send_id",
        title="fields_title",
        currency=pre_created_currency,
        balance=777,
        goal=100,
    )
    jt = JarTransaction.objects.create(
        id="fields_tr_id",
        time=123450,
        description="",
        mcc=pre_created_categories_mso[0],
        amount=-100,
        commission_rate=0,
        currency=pre_created_currency,
        balance=5555,
        hold=True,
        account=jar,
        cashback_amount=0,
    )

    view = MonoJarTransactionViewSet.as_view({"get": "list"})
    response = view(
        api_request(
            "monojartransactions-list",
            tg_id="any_id_fs",
            method_name="get",
            is_admin=False,
            data=None,
            create_new_user=False,
            url_kwargs={},
            query_params={
                "jars": jar.id,
                "fields": "balance,formatted_time",
            },
        )
    )

    expected_time = _time.strftime("%Y-%m-%d %H:%M:%S", _time.localtime(jt.time))
    assert response.data == [{"balance": 5555, "formatted_time": expected_time}]


@pytest.mark.django_db
def test_monojartransactions_time_from_and_fields(
    api_request,
    pre_created_mono_jar_transaction,
    pre_created_currency,
    pre_created_categories_mso,
):
    """Filter by time_from and shrink fields to chart-ready set."""
    User = get_user_model()
    user = User.objects.create_user("any_id_tf", "PassW0rd")
    account = MonoAccount.objects.create(
        user=user, mono_token="unique_token_tf", active=True
    )
    jar = MonoJar.objects.create(
        monoaccount=account,
        id="timefrom_test_jar_id",
        send_id="timefrom_test_send_id",
        title="timefrom_title",
        currency=pre_created_currency,
        balance=100,
        goal=100,
    )

    # Two transactions: one before and one after the cutoff
    before_ts = int(
        _time.mktime(_time.strptime("2025-07-31 23:59:59", "%Y-%m-%d %H:%M:%S"))
    )
    after_ts = int(
        _time.mktime(_time.strptime("2025-08-01 12:00:00", "%Y-%m-%d %H:%M:%S"))
    )

    JarTransaction.objects.create(
        id="old_tr_id",
        time=before_ts,
        description="",
        mcc=pre_created_categories_mso[0],
        amount=-100,
        commission_rate=0,
        currency=pre_created_currency,
        balance=1111,
        hold=True,
        account=jar,
        cashback_amount=0,
    )

    new_tr = JarTransaction.objects.create(
        id="new_tr_id",
        time=after_ts,
        description="",
        mcc=pre_created_categories_mso[0],
        amount=-200,
        commission_rate=0,
        currency=pre_created_currency,
        balance=2222,
        hold=True,
        account=jar,
        cashback_amount=0,
    )

    view = MonoJarTransactionViewSet.as_view({"get": "list"})
    response = view(
        api_request(
            "monojartransactions-list",
            tg_id="any_id_tf",
            method_name="get",
            is_admin=False,
            data=None,
            create_new_user=False,
            url_kwargs={},
            query_params={
                "jars": jar.id,
                "time_from": "2025-08-01",
                "fields": "balance,formatted_time",
            },
        )
    )

    expected_time = _time.strftime("%Y-%m-%d %H:%M:%S", _time.localtime(new_tr.time))
    assert response.data == [{"balance": 2222, "formatted_time": expected_time}]
