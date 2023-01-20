import pytest
from account.views import UserView

import django

django.setup()


@pytest.mark.django_db
@pytest.mark.usefixtures("api_request")
def test_users_get(api_request):
    view = UserView.as_view()

    response = view(
        api_request("users", method_name="get"),
    )
    assert response.status_code == 200
    assert response.data == {"hello": "world"}


@pytest.mark.django_db
@pytest.mark.usefixtures("api_request")
def test_users_creation(api_request):
    view = UserView.as_view()

    response = view(
        api_request("users", method_name="post", data={
            "tg_id": "123",
            "password": "12341234",
            "name": "Some Name"
        })
    )
    assert response.status_code == 201
    assert response.data == {
        'data': {
            'tg_id': '123',
            'name': "Some Name",
        }, 'status': 'ok'
    }

@pytest.mark.django_db
@pytest.mark.usefixtures("pre_created_user")
@pytest.mark.usefixtures("api_request")
def test_users_creation_duplicate(api_request, pre_created_user):
    view = UserView.as_view()

    # Duplicate check
    response = view(
        api_request("users", method_name="post", data={
            "tg_id": "precreated_user_tg_id",
            "password": "precreated_user_password",
            "name": "Some Name"
        })
    )
    assert response.status_code == 400
    assert response.data == {'data': 'user exists', 'status': 'fail'}


