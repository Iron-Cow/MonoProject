from monobank.views import CategoryViewSet
from rest_framework.exceptions import ErrorDetail

from .conftest import Variant

categories_list_variants = [
    (
        "categories retrieve",
        Variant(
            view=CategoryViewSet.as_view({"get": "retrieve"}),
            name="categories-detail",
            is_admin=False,
            tg_id="custom_name",
            url_kwargs={"pk": 2},
            expected={"name": "precreated_category_name2", "symbol": "smbl"},
        ),
    ),
    (
        "categories get",
        Variant(
            view=CategoryViewSet.as_view({"get": "list"}),
            name="categories-list",
            is_admin=False,
            tg_id="custom_name",
            expected=[
                {"name": "precreated_category_name1", "symbol": "smbl"},
                {"name": "precreated_category_name2", "symbol": "smbl"},
            ],
        ),
    ),
    (
        "categories create",
        Variant(
            view=CategoryViewSet.as_view({"post": "create"}),
            name="categories-list",
            method_name="post",
            is_admin=True,
            tg_id="custom_name",
            status_code=405,
            expected={
                "detail": ErrorDetail(
                    string='Method "POST" not allowed.', code="method_not_allowed"
                )
            },
        ),
    ),
    (
        "categories update",
        Variant(
            view=CategoryViewSet.as_view({"put": "update"}),
            name="categories-list",
            method_name="put",
            is_admin=True,
            request_data={"name": "new-category-name", "symbol": "smbl"},
            tg_id="custom_name",
            status_code=405,
            expected={
                "detail": ErrorDetail(
                    string='Method "PUT" not allowed.', code="method_not_allowed"
                )
            },
        ),
    ),
    (
        "categories partial update",
        Variant(
            view=CategoryViewSet.as_view({"patch": "partial_update"}),
            name="categories-list",
            method_name="patch",
            is_admin=True,
            request_data={"name": "new-category-name", "symbol": "smbl"},
            tg_id="custom_name",
            status_code=405,
            expected={
                "detail": ErrorDetail(
                    string='Method "PATCH" not allowed.', code="method_not_allowed"
                )
            },
        ),
    ),
    (
        "categories partial delete",
        Variant(
            view=CategoryViewSet.as_view({"delete": "destroy"}),
            name="categories-detail",
            method_name="delete",
            is_admin=True,
            tg_id="custom_name",
            status_code=405,
            url_kwargs={"pk": 2},
            expected={
                "detail": ErrorDetail(
                    string='Method "DELETE" not allowed.', code="method_not_allowed"
                )
            },
        ),
    ),
]
