import pytest
from django.contrib.auth import get_user_model
from monobank.models import MonoAccount, MonoCard
from monobank.views import MonoCardViewSet
from rest_framework.exceptions import ErrorDetail

from .conftest import Variant

User = get_user_model()

monocards_variants = [
    (
        "monocards retrieve admin",
        Variant(
            view=MonoCardViewSet.as_view({"get": "retrieve"}),
            name="monocards-detail",
            is_admin=True,
            tg_id="admin_name",
            url_kwargs={"pk": "pre_created_card_id"},
            expected={
                "id": "pre_created_card_id",
                "send_id": "pre_created_id",
                "currency": {"code": 980, "name": "UAH", "flag": "🇺🇦", "symbol": "грн"},
                "cashback_type": "pre_created_cashback_type",
                "balance": 100,
                "credit_limit": 0,
                "masked_pan": ["pre_created_masked_pan"],
                "type": "white",
                "iban": "pre_created_iban",
                "owner_name": "User-precreated_user_tg_id",
            },
        ),
    ),
    (
        "monocards retrieve owner",
        Variant(
            view=MonoCardViewSet.as_view({"get": "retrieve"}),
            name="monocards-detail",
            is_admin=False,
            tg_id="precreated_user_tg_id",
            url_kwargs={"pk": "pre_created_card_id"},
            expected={
                "id": "pre_created_card_id",
                "send_id": "pre_created_id",
                "currency": {"code": 980, "name": "UAH", "flag": "🇺🇦", "symbol": "грн"},
                "cashback_type": "pre_created_cashback_type",
                "balance": 100,
                "credit_limit": 0,
                "masked_pan": ["pre_created_masked_pan"],
                "type": "white",
                "iban": "pre_created_iban",
                "owner_name": "User-precreated_user_tg_id",
            },
            create_new_user=False,
        ),
    ),
    (
        "monocards retrieve not owner",
        Variant(
            view=MonoCardViewSet.as_view({"get": "retrieve"}),
            name="monocards-detail",
            is_admin=False,
            tg_id="some_user",
            url_kwargs={"pk": "pre_created_card_id"},
            status_code=404,
            expected={"detail": ErrorDetail(string="Not found.", code="not_found")},
        ),
    ),
]


@pytest.mark.django_db
@pytest.mark.usefixtures("api_request")
@pytest.mark.parametrize("test_name, variant", monocards_variants)
@pytest.mark.usefixtures("pre_created_mono_card")
def test_monocards(api_request, test_name, variant, pre_created_mono_card):
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
        ),
        **variant.url_kwargs,
    )
    assert response.status_code == variant.status_code
    assert response.data == variant.expected


monocards_list_variants = [
    (
        "monocards list admin",
        Variant(
            view=MonoCardViewSet.as_view({"get": "list"}),
            name="monocards-list",
            is_admin=True,
            tg_id="admin_name",
            expected=[
                {
                    "id": "pre_created_card_id",
                    "send_id": "pre_created_id",
                    "currency": {
                        "code": 980,
                        "name": "UAH",
                        "flag": "🇺🇦",
                        "symbol": "грн",
                    },
                    "cashback_type": "pre_created_cashback_type",
                    "balance": 100,
                    "credit_limit": 0,
                    "masked_pan": ["pre_created_masked_pan"],
                    "type": "white",
                    "iban": "pre_created_iban",
                    "owner_name": "User-precreated_user_tg_id",
                },
                {
                    "id": "pre_created_card_id2",
                    "send_id": "pre_created_id2",
                    "currency": {
                        "code": 980,
                        "name": "UAH",
                        "flag": "🇺🇦",
                        "symbol": "грн",
                    },
                    "cashback_type": "pre_created_cashback_type",
                    "balance": 100,
                    "credit_limit": 0,
                    "masked_pan": ["pre_created_masked_pan"],
                    "type": "white",
                    "iban": "pre_created_iban",
                    "owner_name": "User-precreated_user_tg_id",
                },
                {
                    "id": "some_id",
                    "send_id": "some_id",
                    "currency": {
                        "code": 980,
                        "name": "UAH",
                        "flag": "🇺🇦",
                        "symbol": "грн",
                    },
                    "cashback_type": "some_cashback_type",
                    "balance": 100,
                    "credit_limit": 0,
                    "masked_pan": ["some_masked_pan"],
                    "type": "white",
                    "iban": "some_iban",
                    "owner_name": "User-admin_name",
                },
            ],
            create_new_user=False,
        ),
    ),
    (
        "monocards list with query params admin",
        Variant(
            view=MonoCardViewSet.as_view({"get": "list"}),
            name="monocards-list",
            is_admin=True,
            tg_id="admin_name",
            request_data={"users": "precreated_user_tg_id,111"},
            expected=[
                {
                    "id": "pre_created_card_id",
                    "send_id": "pre_created_id",
                    "currency": {
                        "code": 980,
                        "name": "UAH",
                        "flag": "🇺🇦",
                        "symbol": "грн",
                    },
                    "cashback_type": "pre_created_cashback_type",
                    "balance": 100,
                    "credit_limit": 0,
                    "masked_pan": ["pre_created_masked_pan"],
                    "type": "white",
                    "iban": "pre_created_iban",
                    "owner_name": "User-precreated_user_tg_id",
                },
                {
                    "id": "pre_created_card_id2",
                    "send_id": "pre_created_id2",
                    "currency": {
                        "code": 980,
                        "name": "UAH",
                        "flag": "🇺🇦",
                        "symbol": "грн",
                    },
                    "cashback_type": "pre_created_cashback_type",
                    "balance": 100,
                    "credit_limit": 0,
                    "masked_pan": ["pre_created_masked_pan"],
                    "type": "white",
                    "iban": "pre_created_iban",
                    "owner_name": "User-precreated_user_tg_id",
                },
            ],
            create_new_user=False,
        ),
    ),
    (
        "monocards list only owner cards",
        Variant(
            view=MonoCardViewSet.as_view({"get": "list"}),
            name="monocards-list",
            is_admin=False,
            tg_id="custom_name",
            expected=[
                {
                    "id": "some_id",
                    "send_id": "some_id",
                    "currency": {
                        "code": 980,
                        "name": "UAH",
                        "flag": "🇺🇦",
                        "symbol": "грн",
                    },
                    "cashback_type": "some_cashback_type",
                    "balance": 100,
                    "credit_limit": 0,
                    "masked_pan": ["some_masked_pan"],
                    "type": "white",
                    "iban": "some_iban",
                    "owner_name": "User-custom_name",
                },
            ],
            create_new_user=False,
        ),
    ),
]


@pytest.mark.django_db
@pytest.mark.usefixtures("api_request")
@pytest.mark.parametrize("test_name, variant", monocards_list_variants)
@pytest.mark.usefixtures("pre_created_mono_card")
@pytest.mark.usefixtures("pre_created_currency")
def test_monocards_list(
    api_request, test_name, variant, pre_created_mono_card, pre_created_currency
):
    view = variant.view

    user = User.objects.create_user(
        variant.tg_id,
        variant.password,
        is_staff=variant.is_admin,
        is_admin=variant.is_admin,
    )

    account = MonoAccount.objects.create(
        user=user,
        mono_token="unique_token",
        active=True,
    )

    MonoCard.objects.create(
        monoaccount=account,
        id="some_id",
        send_id="some_id",
        currency=pre_created_currency,
        cashback_type="some_cashback_type",
        balance=100,
        credit_limit=0,
        masked_pan=["some_masked_pan"],
        type="white",
        iban="some_iban",
    )

    response = view(
        api_request(
            variant.name,
            tg_id=variant.tg_id,
            method_name=variant.method_name,
            is_admin=variant.is_admin,
            data=variant.request_data,
            create_new_user=variant.create_new_user,
            need_json_dumps=variant.need_json_dumps,
        ),
    )
    assert response.status_code == variant.status_code
    assert response.data == variant.expected
