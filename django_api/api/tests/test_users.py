import pytest
from account.views import UserViewSet
from rest_framework.exceptions import ErrorDetail


from conftest import Variant

users_list_variants = [
    ("admin list", Variant(
        view=UserViewSet.as_view({"get": "list"}),
        name="users-list",
        is_admin=True,
        tg_id="custom_name",
        expected=[
            {"tg_id": "precreated_user_tg_id", "name": "User-precreated_user_tg_id"},
            {"tg_id": "custom_name", "name": "User-custom_name"},
        ]
    )),
    ("not admin list", Variant(
        view=UserViewSet.as_view({"get": "list"}),
        name="users-list",
        is_admin=False,
        tg_id="custom_name",
        status_code=403,
        expected={
            'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                  code='permission_denied')
        },
    )),
    ("not owner/admin retrieve", Variant(
        view=UserViewSet.as_view({"get": "retrieve"}),
        name="users-detail",
        is_admin=True,
        tg_id="custom_name",
        expected={"tg_id": "custom_name", "name": "User-custom_name"},
        url_kwargs={"tg_id": "custom_name"}
    )),
    ("not owner/not admin retrieve", Variant(
        view=UserViewSet.as_view({"get": "retrieve"}),
        name="users-detail",
        is_admin=False,
        tg_id="custom_name",
        status_code=403,
        expected={
            'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                  code='permission_denied')
        },
        url_kwargs={"tg_id": "precreated_user_tg_id"}
    )),
    ("owner/not admin retrieve", Variant(
        view=UserViewSet.as_view({"get": "retrieve"}),
        name="users-detail",
        is_admin=False,
        tg_id="custom_name",
        expected={'tg_id': 'custom_name', 'name': 'User-custom_name'},
        url_kwargs={"tg_id": "custom_name"}
    )),
    ("admin create", Variant(
        view=UserViewSet.as_view({"post": "create"}),
        name="users-list",
        method_name="post",
        is_admin=True,
        tg_id="admin-name",
        format="json",
        request_data={'tg_id': 'custom_name', 'password': "aaaaaa1234", "name": "custom_name"},
        expected={"tg_id": "custom_name",
                  "name": "custom_name"},
        status_code=201,
    )),
    ("not admin create", Variant(
        view=UserViewSet.as_view({"post": "create"}),
        name="users-list",
        method_name="post",
        is_admin=False,
        tg_id="non-admin-name",
        format="json",
        request_data={'tg_id': 'custom_name', 'password': "aaaaaa1234", "name": "custom_name"},
        expected={
            'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                  code='permission_denied')
        },
        status_code=403,
    )),
    ("not owner/admin partial update", Variant(
        view=UserViewSet.as_view({"patch": "partial_update"}),
        name="users-detail",
        method_name="patch",
        is_admin=True,
        tg_id="admin-name",
        format="json",
        request_data={"name": "User-precreated_user_tg_id-new"},
        url_kwargs={"tg_id": "precreated_user_tg_id"},

        expected={"tg_id": "precreated_user_tg_id",
                  "name": "User-precreated_user_tg_id-new"},
        status_code=200,
    )),
    ("owner/not admin partial update", Variant(
        view=UserViewSet.as_view({"patch": "partial_update"}),
        name="users-detail",
        method_name="patch",
        is_admin=False,
        tg_id="custom-user",
        format="json",
        request_data={"name": "custom-user-name-new"},
        url_kwargs={"tg_id": "custom-user"},

        expected={"tg_id": "custom-user",
                  "name": "custom-user-name-new"},
        status_code=200,
    )),
    ("not owner/not admin partial update", Variant(
        view=UserViewSet.as_view({"patch": "partial_update"}),
        name="users-detail",
        method_name="patch",
        is_admin=False,
        tg_id="not-admin-name",
        format="json",
        request_data={"name": "User-precreated_user_tg_id-new"},
        url_kwargs={"tg_id": "precreated_user_tg_id"},

        expected={
            'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                  code='permission_denied')
        },
        status_code=403,
    )),

]


@pytest.mark.django_db
@pytest.mark.usefixtures("api_request")
@pytest.mark.parametrize("test_name, variant", users_list_variants)
@pytest.mark.usefixtures("pre_created_user")
def test_users(api_request, test_name, variant, pre_created_user):
    view = variant.view

    response = view(
        api_request(variant.name, tg_id=variant.tg_id, method_name=variant.method_name, is_admin=variant.is_admin,
                    url_kwargs=variant.url_kwargs, data=variant.request_data), **variant.url_kwargs,
    )
    assert response.status_code == variant.status_code
    assert response.data == variant.expected

# @pytest.mark.django_db
# @pytest.mark.usefixtures("api_request")
# def test_users_creation(api_request):
#     view = UserView.as_view()
#
#     response = view(
#         api_request("users", method_name="post", data={
#             "tg_id": "123",
#             "password": "12341234",
#             "name": "Some Name"
#         })
#     )
#     assert response.status_code == 201
#     assert response.data == {
#         'data': {
#             'tg_id': '123',
#             'name': "Some Name",
#         }, 'status': 'ok'
#     }
#
# @pytest.mark.django_db
# @pytest.mark.usefixtures("pre_created_user")
# @pytest.mark.usefixtures("api_request")
# def test_users_creation_duplicate(api_request, pre_created_user):
#     view = UserView.as_view()
#
#     # Duplicate check
#     response = view(
#         api_request("users", method_name="post", data={
#             "tg_id": "precreated_user_tg_id",
#             "password": "precreated_user_password",
#             "name": "Some Name"
#         })
#     )
#     assert response.status_code == 400
#     assert response.data == {'data': 'user exists', 'status': 'fail'}
#
#
