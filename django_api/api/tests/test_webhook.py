import pytest
from django.contrib.auth import get_user_model
from monobank.models import JarTransaction, MonoTransaction
from monobank.views import TransactionWebhookApiView
from rest_framework.views import Response

from .conftest import Variant

User = get_user_model()

_MSO_FOR_TEST = 5555

webhook_get_variants = [
    (
        "get request every time successful",
        Variant(
            view=TransactionWebhookApiView.as_view(),
            name="webhook",
            method_name="get",
            status_code=200,
        ),
    ),
]


@pytest.mark.django_db
@pytest.mark.parametrize("test_name, variant", webhook_get_variants)
def test_webhook(api_request, test_name, variant):
    response = variant.view(
        api_request(
            variant.name,
            method_name=variant.method_name,
            url_args=(),
        )
    )
    assert response.status_code == variant.status_code


webhook_post_variants = [
    (
        "success: new card transaction",
        Variant(
            view=TransactionWebhookApiView.as_view(),
            name="webhook",
            method_name="post",
            request_data={
                "account": "pre_created_card_id",
                "statementItem": {
                    "amount": 1234,
                    "balance": 12341234,
                    "cashbackAmount": 0,
                    "commissionRate": 0,
                    "currencyCode": 980,
                    "description": "Часткове зняття банки",
                    "hold": True,
                    "id": "44141414",
                    "mcc": 1234,
                    "operationAmount": 19700,
                    "originalMcc": 4829,
                    "receipt_id": "aaa",
                    "comment": "abc",
                    "time": 12341234,
                },
                "type": "StatementItem",
            },
            status_code=201,
            query_params={"token": "abc"},
        ),
        True,
    ),
    (
        "success: existed card transaction",
        Variant(
            view=TransactionWebhookApiView.as_view(),
            name="webhook",
            method_name="post",
            request_data={
                "account": "pre_created_card_id",
                "statementItem": {
                    "amount": 1234,
                    "balance": 12341234,
                    "cashbackAmount": 0,
                    "commissionRate": 0,
                    "currencyCode": 980,
                    "description": "Часткове зняття банки",
                    "hold": True,
                    "id": "pre_created_id",
                    "mcc": 1234,
                    "operationAmount": 19700,
                    "originalMcc": 4829,
                    "receipt_id": "aaa",
                    "comment": "abc",
                    "time": 12341234,
                },
                "type": "StatementItem",
            },
            status_code=200,
            query_params={"token": "abc"},
        ),
        True,
    ),
    (
        "success: new jar transaction",
        Variant(
            view=TransactionWebhookApiView.as_view(),
            name="webhook",
            method_name="post",
            request_data={
                "account": "pre_created_jar_id",
                "statementItem": {
                    "amount": 1234,
                    "balance": 12341234,
                    "cashbackAmount": 0,
                    "commissionRate": 0,
                    "currencyCode": 980,
                    "description": "Часткове зняття банки",
                    "hold": True,
                    "id": "44141414",
                    "mcc": 1234,
                    "operationAmount": 19700,
                    "originalMcc": 4829,
                    "time": 12341234,
                },
                "type": "StatementItem",
            },
            status_code=201,
            query_params={"token": "abc"},
        ),
        True,
    ),
    (
        "success: existed jar transaction",
        Variant(
            view=TransactionWebhookApiView.as_view(),
            name="webhook",
            method_name="post",
            request_data={
                "account": "pre_created_jar_id",
                "statementItem": {
                    "amount": 1234,
                    "balance": 12341234,
                    "cashbackAmount": 0,
                    "commissionRate": 0,
                    "currencyCode": 980,
                    "description": "Часткове зняття банки",
                    "hold": True,
                    "id": "pre_created_id",
                    "mcc": 1234,
                    "operationAmount": 19700,
                    "originalMcc": 4829,
                    "time": 12341234,
                },
                "type": "StatementItem",
            },
            status_code=200,
            query_params={"token": "abc"},
        ),
        True,
    ),
    (
        "error: no token provided",
        Variant(
            view=TransactionWebhookApiView.as_view(),
            name="webhook",
            method_name="post",
            request_data={
                "transaction_type": "card",
                "details": "New card transaction details",
            },
            status_code=403,
            query_params={"tokensomething": "unique_token"},
            expected={"error": "token query param is not specified"},
        ),
        True,
    ),
    (
        "error: invalid token provided",
        Variant(
            view=TransactionWebhookApiView.as_view(),
            name="webhook",
            method_name="post",
            request_data={
                "account": "pre_created_jar_id",
                "statementItem": {
                    "amount": 1234,
                    "balance": 12341234,
                    "cashbackAmount": 0,
                    "commissionRate": 0,
                    "currencyCode": 980,
                    "description": "Часткове зняття банки",
                    "hold": True,
                    "id": "pre_created_id",
                    "mcc": 1234,
                    "operationAmount": 19700,
                    "originalMcc": 4829,
                    "time": 12341234,
                },
                "type": "StatementItem",
            },
            status_code=403,
            query_params={"token": "aasdfasdfasdf"},
            expected={"error": "invalid token or account missmatch"},
        ),
        True,
    ),
    (
        "error: wrong transaction structure",
        Variant(
            view=TransactionWebhookApiView.as_view(),
            name="webhook",
            method_name="post",
            request_data={
                "a": "b",
            },
            status_code=422,
            query_params={"token": "unique_token"},
            expected={"error": f"Wrong request structure"},
        ),
        True,
    ),
]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "test_name, variant, is_should_request_data_check", webhook_post_variants
)
def test_webhook_post(
    api_request,
    pre_created_currency,
    pre_created_categories,
    pre_created_categories_mso,
    pre_created_user,
    pre_created_mono_account,
    pre_created_mono_card,
    pre_created_mono_jar,
    pre_created_mono_transaction,
    pre_created_mono_jar_transaction,
    test_name,
    variant,
    is_should_request_data_check,
):
    view = variant.view
    request = api_request(
        variant.name,
        method_name=variant.method_name,
        data=variant.request_data,
        query_params=variant.query_params,
        need_json_dumps=True,
    )
    response: Response = view(request)
    assert response.status_code == variant.status_code
    if is_should_request_data_check:
        assert response.data == variant.expected

    if 200 <= response.status_code < 300:
        assert (
            MonoTransaction.objects.filter(
                id=variant.request_data.get("statementItem", {}).get("id", "")
            ).exists()
            or JarTransaction.objects.filter(
                id=variant.request_data.get("statementItem", {}).get("id", "")
            ).exists()
        )
