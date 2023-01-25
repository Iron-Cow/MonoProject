
from typing import NamedTuple, List


import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from typing import Callable

from rest_framework.test import APIRequestFactory, force_authenticate
from monobank.models import Category

User = get_user_model()


class Variant(NamedTuple):
    view: Callable
    name: str
    expected: dict | List[dict] = None
    request_data: dict | List[dict] = None
    method_name: str = "get"
    format: str = "json"
    status_code: int = 200
    is_admin: bool = True
    tg_id: str = "username"
    password = "PassW0rd",
    url_args: tuple = tuple()
    url_kwargs: dict = dict()


@pytest.fixture
def api_request():
    def get_view_by_name(
        view_name,
        method_name="get",
        url_args=None,
        url_kwargs=None,
        data=None,
        format=None,
        tg_id="username",
        password="PassW0rd",
        is_staff=False,
        is_admin=False,
    ):
        user = User.objects.create_user(tg_id, password, is_staff=is_admin, is_admin=is_admin)
        factory = APIRequestFactory()
        url = reverse(view_name, args=url_args, kwargs=url_kwargs)
        factory_method = getattr(factory, method_name)
        request = factory_method(url, data=data, format=format)
        force_authenticate(request, user=user)

        return request

    return get_view_by_name

@pytest.fixture
def pre_created_user(db) -> User:
    precreated_user = User.objects.create_user(
        tg_id="precreated_user_tg_id",
        password="precreated_user_password",
    )
    return precreated_user

@pytest.fixture
def pre_created_categories(db):
    Category.objects.create(
        name="precreated_category_name1",
        symbol="smbl",
        user_defined=False,
    )
    Category.objects.create(
        name="precreated_category_name2",
        symbol="smbl",
        user_defined=False,
    )

