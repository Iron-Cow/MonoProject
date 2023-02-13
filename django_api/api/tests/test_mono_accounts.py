from unittest.mock import patch

import pytest

from monobank.models import MonoAccount, MonoCard
from monobank.views import MonoAccountViewSet
from rest_framework.exceptions import ErrorDetail

from conftest import Variant, NO_PERMISSION_ERROR

monoaccounts_list_variants = [
    (
        "monousers retrieve admin",
        Variant(
            view=MonoAccountViewSet.as_view({"get": "retrieve"}),
            name="monoaccounts-detail",
            is_admin=True,
            tg_id="admin_name",
            url_kwargs={"pk": 1},
            expected={
                "user": "precreated_user_tg_id",
                "mono_token": "abc",
                "active": True,
            },
        ),
    ),
    (
        "monousers retrieve not admin",
        Variant(
            view=MonoAccountViewSet.as_view({"get": "retrieve"}),
            name="monoaccounts-detail",
            is_admin=False,
            tg_id="custom_name",
            url_kwargs={"pk": 1},
            expected=NO_PERMISSION_ERROR,
            status_code=403,
        ),
    ),
    (
        "monousers get admin",
        Variant(
            view=MonoAccountViewSet.as_view({"get": "list"}),
            name="monoaccounts-list",
            is_admin=True,
            tg_id="admin_name",
            expected=[
                {
                    "user": "precreated_user_tg_id",
                    "mono_token": "abc",
                    "active": True,
                },
            ],
        ),
    ),
    (
        "monousers get not admin",
        Variant(
            view=MonoAccountViewSet.as_view({"get": "list"}),
            name="monoaccounts-list",
            is_admin=False,
            tg_id="custom_name",
            expected=NO_PERMISSION_ERROR,
            status_code=403,
        ),
    ),
    (
        "monousers create admin",
        Variant(
            view=MonoAccountViewSet.as_view({"post": "create"}),
            name="monoaccounts-list",
            method_name="post",
            is_admin=True,
            tg_id="admin_name",
            request_data={"user": "admin_name", "mono_token": "unique_token"},
            format="json",
            status_code=201,
            expected={"user": "admin_name", "mono_token": "unique_token"},
            need_json_dumps=True,
        ),
    ),
    (
        "monousers update admin",
        Variant(
            view=MonoAccountViewSet.as_view({"put": "update"}),
            name="monoaccounts-list",
            method_name="put",
            is_admin=True,
            request_data={"name": "new-category-name", "symbol": "smbl"},
            tg_id="admin_name",
            status_code=405,
            expected={
                "detail": ErrorDetail(
                    string='Method "PUT" not allowed.', code="method_not_allowed"
                )
            },
        ),
    ),
    (
        "monousers partial update admin",
        Variant(
            view=MonoAccountViewSet.as_view({"patch": "partial_update"}),
            name="monoaccounts-list",
            method_name="patch",
            is_admin=True,
            request_data={"name": "new-category-name", "symbol": "smbl"},
            tg_id="admin_name",
            status_code=405,
            expected={
                "detail": ErrorDetail(
                    string='Method "PATCH" not allowed.', code="method_not_allowed"
                )
            },
        ),
    ),
    (
        "monousers partial delete admin",
        Variant(
            view=MonoAccountViewSet.as_view({"delete": "destroy"}),
            name="monoaccounts-detail",
            method_name="delete",
            is_admin=True,
            tg_id="admin_name",
            status_code=405,
            url_kwargs={"pk": 1},
            expected={
                "detail": ErrorDetail(
                    string='Method "DELETE" not allowed.', code="method_not_allowed"
                )
            },
        ),
    ),
]


@pytest.mark.django_db
@pytest.mark.usefixtures("api_request")
@pytest.mark.parametrize("test_name, variant", monoaccounts_list_variants)
@pytest.mark.usefixtures("pre_created_mono_account")
def test_monousers(
    api_request, test_name, variant, monkeypatch, pre_created_mono_account
):
    monkeypatch.setattr(MonoAccount, "get_cards_jars", lambda x: {})
    view = variant.view

    response = view(
        api_request(
            variant.name,
            tg_id=variant.tg_id,
            method_name=variant.method_name,
            is_admin=variant.is_admin,
            url_kwargs=variant.url_kwargs,
            data=variant.request_data,
            need_json_dumps=variant.need_json_dumps,
        ),
        **variant.url_kwargs,
    )
    assert response.status_code == variant.status_code
    assert response.data == variant.expected
