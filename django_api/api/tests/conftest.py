from typing import NamedTuple, List
from rest_framework.exceptions import ErrorDetail

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from typing import Callable

from rest_framework.test import APIRequestFactory, force_authenticate
from monobank.models import Category, MonoAccount, MonoCard, MonoJar

User = get_user_model()

NO_PERMISSION_ERROR = {
    "detail": ErrorDetail(
        string="You do not have permission to perform this action.",
        code="permission_denied",
    )
}


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
    password = "PassW0rd"
    url_args: tuple = tuple()
    url_kwargs: dict = dict()
    create_new_user: bool = True


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
        create_new_user=True,
    ):
        if create_new_user:
            user = User.objects.create_user(
                tg_id, password, is_staff=is_admin, is_admin=is_admin
            )
        else:
            user = User.objects.get(tg_id=tg_id)
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


@pytest.fixture
def pre_created_mono_account(db, pre_created_user):
    account = MonoAccount.objects.create(
        user=pre_created_user,
        mono_token="abc",
        active=True,
    )
    return account


@pytest.fixture
def pre_created_mono_card(db, pre_created_mono_account):
    monocard = MonoCard.objects.create(
        monoaccount=pre_created_mono_account,
        id="pre_created_id",
        send_id="pre_created_id",
        currency_code=980,
        cashback_type="pre_created_cashback_type",
        balance=100,
        credit_limit=0,
        masked_pan=["pre_created_masked_pan"],
        type="white",
        iban="pre_created_iban",
    )
    monocard2 = MonoCard.objects.create(
        monoaccount=pre_created_mono_account,
        id="pre_created_id2",
        send_id="pre_created_id2",
        currency_code=980,
        cashback_type="pre_created_cashback_type",
        balance=100,
        credit_limit=0,
        masked_pan=["pre_created_masked_pan"],
        type="white",
        iban="pre_created_iban",
    )
    return monocard, monocard2


@pytest.fixture
def pre_created_mono_jar(db, pre_created_mono_account):
    monojar = MonoJar.objects.create(
        monoaccount=pre_created_mono_account,
        id="pre_created_id",
        send_id="pre_created_id",
        title="pre_created_title",
        currency_code=980,
        balance=1000,
        goal=1001,
    )
    monojar2 = MonoJar.objects.create(
        monoaccount=pre_created_mono_account,
        id="pre_created_id2",
        send_id="pre_created_id2",
        title="pre_created_title2",
        currency_code=980,
        balance=2000,
        goal=2001,
    )
    return monojar, monojar2
