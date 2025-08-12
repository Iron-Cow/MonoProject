import pytest
from django.contrib.auth import get_user_model
from monobank.models import MonoAccount, MonoJar
from monobank.views import MonoJarViewSet
from rest_framework.exceptions import ErrorDetail

from .conftest import Variant

User = get_user_model()

monojars_variants = [
    (
        "monojars retrieve admin",
        Variant(
            view=MonoJarViewSet.as_view({"get": "retrieve"}),
            name="monojars-detail",
            is_admin=True,
            tg_id="admin_name",
            url_kwargs={"pk": "pre_created_jar_id"},
            expected={
                "id": "pre_created_jar_id",
                "send_id": "pre_created_id",
                "title": "pre_created_title",
                "currency": {"code": 980, "name": "UAH", "flag": "🇺🇦", "symbol": "грн"},
                "balance": 1000,
                "goal": 1001,
                "owner_name": "User-precreated_user_tg_id",
                "is_budget": False,
            },
        ),
    ),
    (
        "monojars retrieve owner",
        Variant(
            view=MonoJarViewSet.as_view({"get": "retrieve"}),
            name="monojars-detail",
            is_admin=False,
            tg_id="precreated_user_tg_id",
            url_kwargs={"pk": "pre_created_jar_id"},
            expected={
                "id": "pre_created_jar_id",
                "send_id": "pre_created_id",
                "title": "pre_created_title",
                "currency": {"code": 980, "name": "UAH", "flag": "🇺🇦", "symbol": "грн"},
                "balance": 1000,
                "goal": 1001,
                "owner_name": "User-precreated_user_tg_id",
                "is_budget": False,
            },
            create_new_user=False,
        ),
    ),
    (
        "monojars retrieve not owner",
        Variant(
            view=MonoJarViewSet.as_view({"get": "retrieve"}),
            name="monojars-detail",
            is_admin=False,
            tg_id="some_user",
            url_kwargs={"pk": "pre_created_id"},
            status_code=404,
            expected={"detail": ErrorDetail(string="Not found.", code="not_found")},
        ),
    ),
]


@pytest.mark.django_db
@pytest.mark.usefixtures("api_request")
@pytest.mark.parametrize("test_name, variant", monojars_variants)
@pytest.mark.usefixtures("pre_created_mono_jar")
def test_monojars(api_request, test_name, variant, pre_created_mono_card):
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


monojars_list_variants = [
    (
        "monojars list admin",
        Variant(
            view=MonoJarViewSet.as_view({"get": "list"}),
            name="monojars-list",
            is_admin=True,
            tg_id="admin_name",
            expected=[
                {
                    "id": "family_jar_id",
                    "send_id": "family_jar_send_id",
                    "title": "family_jar_title",
                    "currency": {
                        "code": 980,
                        "name": "UAH",
                        "flag": "🇺🇦",
                        "symbol": "грн",
                    },
                    "balance": 4000,
                    "goal": 4001,
                    "owner_name": "User-family_member_tg_id",
                    "is_budget": False,
                },
                {
                    "id": "pre_created_jar_id",
                    "send_id": "pre_created_id",
                    "title": "pre_created_title",
                    "currency": {
                        "code": 980,
                        "name": "UAH",
                        "flag": "🇺🇦",
                        "symbol": "грн",
                    },
                    "balance": 1000,
                    "goal": 1001,
                    "owner_name": "User-precreated_user_tg_id",
                    "is_budget": False,
                },
                {
                    "id": "pre_created_jar_id2",
                    "send_id": "pre_created_id2",
                    "title": "pre_created_title2",
                    "currency": {
                        "code": 980,
                        "name": "UAH",
                        "flag": "🇺🇦",
                        "symbol": "грн",
                    },
                    "balance": 2000,
                    "goal": 2001,
                    "owner_name": "User-precreated_user_tg_id",
                    "is_budget": False,
                },
                {
                    "id": "some_id",
                    "send_id": "some_id",
                    "title": "some_title",
                    "currency": {
                        "code": 980,
                        "name": "UAH",
                        "flag": "🇺🇦",
                        "symbol": "грн",
                    },
                    "balance": 3000,
                    "goal": 3001,
                    "owner_name": "User-admin_name",
                    "is_budget": False,
                },
            ],
            create_new_user=False,
        ),
    ),
    (
        "monojars list with query params admin",
        Variant(
            view=MonoJarViewSet.as_view({"get": "list"}),
            name="monojars-list",
            is_admin=True,
            tg_id="admin_name",
            request_data={"users": "precreated_user_tg_id,111"},
            expected=[
                {
                    "id": "pre_created_jar_id",
                    "send_id": "pre_created_id",
                    "title": "pre_created_title",
                    "currency": {
                        "code": 980,
                        "name": "UAH",
                        "flag": "🇺🇦",
                        "symbol": "грн",
                    },
                    "balance": 1000,
                    "goal": 1001,
                    "owner_name": "User-precreated_user_tg_id",
                    "is_budget": False,
                },
                {
                    "id": "pre_created_jar_id2",
                    "send_id": "pre_created_id2",
                    "title": "pre_created_title2",
                    "currency": {
                        "code": 980,
                        "name": "UAH",
                        "flag": "🇺🇦",
                        "symbol": "грн",
                    },
                    "balance": 2000,
                    "goal": 2001,
                    "owner_name": "User-precreated_user_tg_id",
                    "is_budget": False,
                },
            ],
            create_new_user=False,
        ),
    ),
    (
        "monojars list only owner cards",
        Variant(
            view=MonoJarViewSet.as_view({"get": "list"}),
            name="monojars-list",
            is_admin=False,
            tg_id="custom_name",
            expected=[
                {
                    "id": "some_id",
                    "send_id": "some_id",
                    "title": "some_title",
                    "currency": {
                        "code": 980,
                        "name": "UAH",
                        "flag": "🇺🇦",
                        "symbol": "грн",
                    },
                    "balance": 3000,
                    "goal": 3001,
                    "owner_name": "User-custom_name",
                    "is_budget": False,
                },
            ],
            create_new_user=False,
        ),
    ),
    (
        "monojars list admin with with_family=1 expands users",
        Variant(
            view=MonoJarViewSet.as_view({"get": "list"}),
            name="monojars-list",
            is_admin=True,
            tg_id="admin_name",
            request_data={"users": "precreated_user_tg_id", "with_family": 1},
            expected=[
                {
                    "id": "family_jar_id",
                    "send_id": "family_jar_send_id",
                    "title": "family_jar_title",
                    "currency": {
                        "code": 980,
                        "name": "UAH",
                        "flag": "🇺🇦",
                        "symbol": "грн",
                    },
                    "balance": 4000,
                    "goal": 4001,
                    "owner_name": "User-family_member_tg_id",
                    "is_budget": False,
                },
                {
                    "id": "pre_created_jar_id",
                    "send_id": "pre_created_id",
                    "title": "pre_created_title",
                    "currency": {
                        "code": 980,
                        "name": "UAH",
                        "flag": "🇺🇦",
                        "symbol": "грн",
                    },
                    "balance": 1000,
                    "goal": 1001,
                    "owner_name": "User-precreated_user_tg_id",
                    "is_budget": False,
                },
                {
                    "id": "pre_created_jar_id2",
                    "send_id": "pre_created_id2",
                    "title": "pre_created_title2",
                    "currency": {
                        "code": 980,
                        "name": "UAH",
                        "flag": "🇺🇦",
                        "symbol": "грн",
                    },
                    "balance": 2000,
                    "goal": 2001,
                    "owner_name": "User-precreated_user_tg_id",
                    "is_budget": False,
                },
            ],
            create_new_user=False,
        ),
    ),
    (
        "monojars list non-admin with_family=1 filters to accessible",
        Variant(
            view=MonoJarViewSet.as_view({"get": "list"}),
            name="monojars-list",
            is_admin=False,
            tg_id="precreated_user_tg_id",
            request_data={"users": "precreated_user_tg_id", "with_family": 1},
            expected=[
                {
                    "id": "family_jar_id",
                    "send_id": "family_jar_send_id",
                    "title": "family_jar_title",
                    "currency": {
                        "code": 980,
                        "name": "UAH",
                        "flag": "🇺🇦",
                        "symbol": "грн",
                    },
                    "balance": 4000,
                    "goal": 4001,
                    "owner_name": "User-family_member_tg_id",
                    "is_budget": False,
                },
                {
                    "id": "pre_created_jar_id",
                    "send_id": "pre_created_id",
                    "title": "pre_created_title",
                    "currency": {
                        "code": 980,
                        "name": "UAH",
                        "flag": "🇺🇦",
                        "symbol": "грн",
                    },
                    "balance": 1000,
                    "goal": 1001,
                    "owner_name": "User-precreated_user_tg_id",
                    "is_budget": False,
                },
                {
                    "id": "pre_created_jar_id2",
                    "send_id": "pre_created_id2",
                    "title": "pre_created_title2",
                    "currency": {
                        "code": 980,
                        "name": "UAH",
                        "flag": "🇺🇦",
                        "symbol": "грн",
                    },
                    "balance": 2000,
                    "goal": 2001,
                    "owner_name": "User-precreated_user_tg_id",
                    "is_budget": False,
                },
            ],
            create_new_user=False,
        ),
    ),
]


@pytest.mark.django_db
@pytest.mark.usefixtures("api_request")
@pytest.mark.parametrize("test_name, variant", monojars_list_variants)
@pytest.mark.usefixtures("pre_created_mono_jar")
@pytest.mark.usefixtures("pre_created_currency")
@pytest.mark.usefixtures("pre_created_family_for_precreated_user")
def test_monojars_list(
    api_request, test_name, variant, pre_created_mono_card, pre_created_currency
):
    view = variant.view

    # Create or reuse user based on test variant
    user = None
    if not variant.create_new_user:
        user = User.objects.filter(tg_id=variant.tg_id).first()
    if user is None:
        user = User.objects.create_user(
            variant.tg_id,
            variant.password,
            is_staff=variant.is_admin,
            is_admin=variant.is_admin,
        )

    # Ensure account and a sample jar exist only if absent (avoid duplications for precreated users)
    if not MonoAccount.objects.filter(user=user).exists():
        account = MonoAccount.objects.create(
            user=user,
            mono_token="unique_token",
            active=True,
        )

        MonoJar.objects.create(
            monoaccount=account,
            id="some_id",
            send_id="some_id",
            title="some_title",
            currency=pre_created_currency,
            balance=3000,
            goal=3001,
        )

    response = view(
        api_request(
            variant.name,
            tg_id=variant.tg_id,
            method_name=variant.method_name,
            is_admin=variant.is_admin,
            data=variant.request_data,
            create_new_user=variant.create_new_user,
        ),
    )
    assert response.status_code == variant.status_code
    assert response.data == variant.expected


monojars_set_budget_variants = [
    (
        "monojars set budget status admin",
        Variant(
            view=MonoJarViewSet.as_view({"patch": "set_budget_status"}),
            name="monojars-set-budget-status",
            method_name="patch",
            is_admin=True,
            tg_id="admin_name",
            url_kwargs={"pk": "pre_created_jar_id"},
            request_data={"is_budget": True},
            need_json_dumps=True,
            expected={
                "id": "pre_created_jar_id",
                "send_id": "pre_created_id",
                "title": "pre_created_title",
                "currency": {"code": 980, "name": "UAH", "flag": "🇺🇦", "symbol": "грн"},
                "balance": 1000,
                "goal": 1001,
                "owner_name": "User-precreated_user_tg_id",
                "is_budget": True,
            },
        ),
    ),
    (
        "monojars set budget status owner",
        Variant(
            view=MonoJarViewSet.as_view({"patch": "set_budget_status"}),
            name="monojars-set-budget-status",
            method_name="patch",
            is_admin=False,
            tg_id="precreated_user_tg_id",
            url_kwargs={"pk": "pre_created_jar_id"},
            request_data={"is_budget": True},
            need_json_dumps=True,
            expected={
                "id": "pre_created_jar_id",
                "send_id": "pre_created_id",
                "title": "pre_created_title",
                "currency": {"code": 980, "name": "UAH", "flag": "🇺🇦", "symbol": "грн"},
                "balance": 1000,
                "goal": 1001,
                "owner_name": "User-precreated_user_tg_id",
                "is_budget": True,
            },
            create_new_user=False,
        ),
    ),
    (
        "monojars set budget status not owner",
        Variant(
            view=MonoJarViewSet.as_view({"patch": "set_budget_status"}),
            name="monojars-set-budget-status",
            method_name="patch",
            is_admin=False,
            tg_id="some_user",
            url_kwargs={"pk": "pre_created_jar_id"},
            request_data={"is_budget": True},
            need_json_dumps=True,
            status_code=404,
            expected={"detail": ErrorDetail(string="Not found.", code="not_found")},
        ),
    ),
    (
        "monojars set budget status missing param",
        Variant(
            view=MonoJarViewSet.as_view({"patch": "set_budget_status"}),
            name="monojars-set-budget-status",
            method_name="patch",
            is_admin=True,
            tg_id="admin_name",
            url_kwargs={"pk": "pre_created_jar_id"},
            request_data={},
            need_json_dumps=True,
            status_code=400,
            expected={"error": "is_budget parameter is required"},
        ),
    ),
    (
        "monojars set budget status string false",
        Variant(
            view=MonoJarViewSet.as_view({"patch": "set_budget_status"}),
            name="monojars-set-budget-status",
            method_name="patch",
            is_admin=True,
            tg_id="admin_name",
            url_kwargs={"pk": "pre_created_jar_id"},
            request_data={"is_budget": False},
            need_json_dumps=True,
            expected={
                "id": "pre_created_jar_id",
                "send_id": "pre_created_id",
                "title": "pre_created_title",
                "currency": {"code": 980, "name": "UAH", "flag": "🇺🇦", "symbol": "грн"},
                "balance": 1000,
                "goal": 1001,
                "owner_name": "User-precreated_user_tg_id",
                "is_budget": False,
            },
        ),
    ),
]


@pytest.mark.django_db
@pytest.mark.usefixtures("api_request")
@pytest.mark.parametrize("test_name, variant", monojars_set_budget_variants)
@pytest.mark.usefixtures("pre_created_mono_jar")
def test_monojars_set_budget_status(
    api_request, test_name, variant, pre_created_mono_card
):
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
            need_json_dumps=variant.need_json_dumps,
        ),
        **variant.url_kwargs,
    )
    assert response.status_code == variant.status_code
    assert response.data == variant.expected
