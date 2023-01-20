import tempfile
from copy import deepcopy
from typing import Dict, List, NamedTuple, Optional, Type, Union
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.urls import reverse

from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.utils.serializer_helpers import OrderedDict, ReturnDict, ReturnList
from rest_framework.views import APIView

User = get_user_model()

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
        user = User.objects.create_user(tg_id, password, is_staff=is_staff, is_admin=is_admin)
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
