from unittest.mock import patch

import pytest
from account.views import (
    FamilyInviteCodeApiView,
    FamilyInviteDecisionApiView,
    FamilyInviteProposalApiView,
)
from django.contrib.auth import get_user_model

from .conftest import Variant

User = get_user_model()


# Test variants for family invite code generation
family_code_variants = [
    (
        "family code generate success",
        Variant(
            view=FamilyInviteCodeApiView.as_view(),
            name="family-code-generate",
            method_name="post",
            is_admin=False,
            tg_id="test_user_123",
            url_kwargs={"tg_id": "test_user_123"},
            expected={"code": "ABC123", "expires_in": 600},
            status_code=201,
        ),
    ),
    (
        "family code generate user not found",
        Variant(
            view=FamilyInviteCodeApiView.as_view(),
            name="family-code-generate",
            method_name="post",
            is_admin=False,
            tg_id="test_user_123",
            url_kwargs={"tg_id": "nonexistent_user"},
            status_code=404,
        ),
    ),
]


@pytest.mark.parametrize("test_name, variant", family_code_variants)
def test_family_code_generation(test_name, variant, api_request, pre_created_user):
    """Test family invite code generation endpoints"""
    # Mock cache for testing
    mock_cache = {}

    def mock_get(key):
        return mock_cache.get(key)

    def mock_set(key, value, timeout=None):
        mock_cache[key] = value

    def mock_delete(key):
        mock_cache.pop(key, None)

    with patch("account.views.cache") as mock_cache_obj:
        mock_cache_obj.get.side_effect = mock_get
        mock_cache_obj.set.side_effect = mock_set
        mock_cache_obj.delete.side_effect = mock_delete

        with patch("account.views._generate_code", return_value="ABC123"):
            request = api_request(
                view_name=variant.name,
                method_name=variant.method_name,
                tg_id=variant.tg_id,
                is_admin=variant.is_admin,
                url_kwargs=variant.url_kwargs,
                data=variant.request_data or {},
                create_new_user=variant.create_new_user,
                need_json_dumps=True,
            )

            response = variant.view(request, **variant.url_kwargs)

            assert response.status_code == variant.status_code

            if variant.expected and response.status_code < 400:
                response_data = response.data
                for key, expected_value in variant.expected.items():
                    assert key in response_data
                    if key == "code":
                        assert len(response_data[key]) == 6
                    elif key == "expires_in":
                        assert response_data[key] == expected_value


# Test variants for family invite proposals
family_proposal_variants = [
    (
        "family proposal success",
        Variant(
            view=FamilyInviteProposalApiView.as_view(),
            name="family-invite-proposal",
            method_name="post",
            is_admin=False,
            tg_id="inviter_123",
            request_data={"inviter_tg_id": "inviter_123", "code": "VALID123"},
            status_code=201,
        ),
    ),
    (
        "family proposal invalid code",
        Variant(
            view=FamilyInviteProposalApiView.as_view(),
            name="family-invite-proposal",
            method_name="post",
            is_admin=False,
            tg_id="inviter_123",
            request_data={"inviter_tg_id": "inviter_123", "code": "INVALID"},
            status_code=404,
        ),
    ),
    (
        "family proposal missing data",
        Variant(
            view=FamilyInviteProposalApiView.as_view(),
            name="family-invite-proposal",
            method_name="post",
            is_admin=False,
            tg_id="inviter_123",
            request_data={"inviter_tg_id": "inviter_123"},  # Missing code
            status_code=400,
        ),
    ),
]


@pytest.mark.parametrize("test_name, variant", family_proposal_variants)
def test_family_invite_proposal(test_name, variant, api_request, pre_created_user):
    """Test family invite proposal endpoints"""
    # Create a second user for testing
    member_user = User.objects.create_user(tg_id="member_456", password="test123")

    # Mock cache for testing
    mock_cache = {}

    # Pre-populate cache with valid code for success test
    if "success" in test_name:
        mock_cache["family_code:VALID123"] = "member_456"

    def mock_get(key):
        return mock_cache.get(key)

    def mock_set(key, value, timeout=None):
        mock_cache[key] = value

    def mock_delete(key):
        mock_cache.pop(key, None)

    with patch("account.views.cache") as mock_cache_obj:
        mock_cache_obj.get.side_effect = mock_get
        mock_cache_obj.set.side_effect = mock_set
        mock_cache_obj.delete.side_effect = mock_delete

        with patch("account.views.uuid.uuid4") as mock_uuid:
            mock_uuid.return_value.hex = "test-invite-123"

            request = api_request(
                view_name=variant.name,
                method_name=variant.method_name,
                tg_id=variant.tg_id,
                is_admin=variant.is_admin,
                data=variant.request_data or {},
                create_new_user=variant.create_new_user,
                need_json_dumps=True,
            )

            response = variant.view(request)

            assert response.status_code == variant.status_code

            if variant.status_code == 201:
                response_data = response.data
                assert "invite_id" in response_data
                assert response_data["inviter_tg_id"] == "inviter_123"
                assert response_data["member_tg_id"] == "member_456"
                assert response_data["status"] == "pending"


# Test variants for family invite decisions
family_decision_variants = [
    (
        "family decision accept",
        Variant(
            view=FamilyInviteDecisionApiView.as_view(),
            name="family-invite-decision",
            method_name="post",
            is_admin=False,
            tg_id="member_456",
            request_data={
                "invite_id": "test-invite-123",
                "decision": "accept",
                "actor_tg_id": "member_456",
            },
            status_code=200,
        ),
    ),
    (
        "family decision decline",
        Variant(
            view=FamilyInviteDecisionApiView.as_view(),
            name="family-invite-decision",
            method_name="post",
            is_admin=False,
            tg_id="member_456",
            request_data={
                "invite_id": "test-invite-123",
                "decision": "decline",
                "actor_tg_id": "member_456",
            },
            status_code=200,
        ),
    ),
    (
        "family decision forbidden actor",
        Variant(
            view=FamilyInviteDecisionApiView.as_view(),
            name="family-invite-decision",
            method_name="post",
            is_admin=False,
            tg_id="wrong_user",
            request_data={
                "invite_id": "test-invite-123",
                "decision": "accept",
                "actor_tg_id": "wrong_user",
            },
            status_code=403,
        ),
    ),
    (
        "family decision not found",
        Variant(
            view=FamilyInviteDecisionApiView.as_view(),
            name="family-invite-decision",
            method_name="post",
            is_admin=False,
            tg_id="member_456",
            request_data={
                "invite_id": "nonexistent",
                "decision": "accept",
                "actor_tg_id": "member_456",
            },
            status_code=404,
        ),
    ),
    (
        "family decision invalid decision",
        Variant(
            view=FamilyInviteDecisionApiView.as_view(),
            name="family-invite-decision",
            method_name="post",
            is_admin=False,
            tg_id="member_456",
            request_data={
                "invite_id": "test-invite-123",
                "decision": "maybe",  # Invalid
                "actor_tg_id": "member_456",
            },
            status_code=400,
        ),
    ),
]


@pytest.mark.parametrize("test_name, variant", family_decision_variants)
def test_family_invite_decision(test_name, variant, api_request, pre_created_user):
    """Test family invite decision endpoints"""
    # Create users for testing
    inviter_user = User.objects.create_user(tg_id="inviter_123", password="test123")
    member_user = User.objects.create_user(tg_id="member_456", password="test123")
    wrong_user = User.objects.create_user(tg_id="wrong_user", password="test123")

    # Mock cache for testing
    mock_cache = {}

    # Pre-populate cache with invite for most tests
    if "not found" not in test_name:
        mock_cache["family_invite:test-invite-123"] = {
            "invite_id": "test-invite-123",
            "inviter_tg_id": "inviter_123",
            "member_tg_id": "member_456",
            "status": "pending",
        }

    def mock_get(key):
        return mock_cache.get(key)

    def mock_set(key, value, timeout=None):
        mock_cache[key] = value

    def mock_delete(key):
        mock_cache.pop(key, None)

    with patch("account.views.cache") as mock_cache_obj:
        mock_cache_obj.get.side_effect = mock_get
        mock_cache_obj.set.side_effect = mock_set
        mock_cache_obj.delete.side_effect = mock_delete

        request = api_request(
            view_name=variant.name,
            method_name=variant.method_name,
            tg_id=variant.tg_id,
            is_admin=variant.is_admin,
            data=variant.request_data or {},
            create_new_user=variant.create_new_user,
            need_json_dumps=True,
        )

        response = variant.view(request)

        assert response.status_code == variant.status_code

        if variant.status_code == 200:
            response_data = response.data
            assert "status" in response_data
            if "accept" in test_name:
                assert response_data["status"] == "accepted"
                # Verify family relationship was created
                inviter_user.refresh_from_db()
                member_user.refresh_from_db()
                assert member_user in inviter_user.family_members.all()
            elif "decline" in test_name:
                assert response_data["status"] == "declined"


def test_family_code_reuse_existing(api_request, pre_created_user):
    """Test that existing valid code is reused"""
    # Mock cache for testing
    mock_cache = {"family_code_user:test_user_123": "EXISTING123"}

    def mock_get(key):
        return mock_cache.get(key)

    def mock_set(key, value, timeout=None):
        mock_cache[key] = value

    with patch("account.views.cache") as mock_cache_obj:
        mock_cache_obj.get.side_effect = mock_get
        mock_cache_obj.set.side_effect = mock_set

        request = api_request(
            view_name="family-code-generate",
            method_name="post",
            tg_id="test_user_123",
            is_admin=False,
            url_kwargs={"tg_id": "test_user_123"},
            create_new_user=True,
        )

        response = FamilyInviteCodeApiView.as_view()(request, tg_id="test_user_123")

        assert response.status_code == 200
        assert response.data["code"] == "EXISTING123"


def test_family_code_collision_handling(api_request, pre_created_user):
    """Test that code generation handles collisions"""
    # Mock cache for testing
    mock_cache = {"family_code:COLLISION": "other_user"}

    def mock_get(key):
        return mock_cache.get(key)

    def mock_set(key, value, timeout=None):
        mock_cache[key] = value

    with patch("account.views.cache") as mock_cache_obj:
        mock_cache_obj.get.side_effect = mock_get
        mock_cache_obj.set.side_effect = mock_set

        with patch("account.views._generate_code") as mock_generate:
            # Return collision first 4 times, then unique
            mock_generate.side_effect = [
                "COLLISION",
                "COLLISION",
                "COLLISION",
                "COLLISION",
                "UNIQUE123",
            ]

            request = api_request(
                view_name="family-code-generate",
                method_name="post",
                tg_id="test_user_123",
                is_admin=False,
                url_kwargs={"tg_id": "test_user_123"},
                create_new_user=True,
                need_json_dumps=True,
            )

            response = FamilyInviteCodeApiView.as_view()(request, tg_id="test_user_123")

            assert response.status_code == 201
            assert response.data["code"] == "UNIQUE123"


def test_family_code_max_retries_exceeded(api_request, pre_created_user):
    """Test code generation failure after max retries"""
    # Mock cache for testing
    mock_cache = {"family_code:COLLISION": "other_user"}

    def mock_get(key):
        return mock_cache.get(key)

    def mock_set(key, value, timeout=None):
        mock_cache[key] = value

    with patch("account.views.cache") as mock_cache_obj:
        mock_cache_obj.get.side_effect = mock_get
        mock_cache_obj.set.side_effect = mock_set

        with patch("account.views._generate_code", return_value="COLLISION"):
            request = api_request(
                view_name="family-code-generate",
                method_name="post",
                tg_id="test_user_123",
                is_admin=False,
                url_kwargs={"tg_id": "test_user_123"},
                create_new_user=True,
                need_json_dumps=True,
            )

            response = FamilyInviteCodeApiView.as_view()(request, tg_id="test_user_123")

            assert response.status_code == 500
            assert response.data["error"] == "failed to generate code"
