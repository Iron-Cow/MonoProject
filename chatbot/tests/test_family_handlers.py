import asyncio
import types
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.types import InlineKeyboardButton

from .testsupport import DummyResponse


@pytest.mark.asyncio
async def test_family_menu_command(mock_config, bot_stub, dp_module):
    """Test /family command shows menu with options"""
    message = types.SimpleNamespace(
        chat=types.SimpleNamespace(id=123),
        from_user=types.SimpleNamespace(id=456),
    )

    await dp_module.family_menu(message)

    assert len(bot_stub.sent) == 1
    sent_msg = bot_stub.sent[0]
    assert sent_msg.chat_id == 123
    assert "Family linking options" in sent_msg.text
    assert "Generate a code" in sent_msg.text
    assert "Enter code to invite" in sent_msg.text
    assert sent_msg.reply_markup is not None


@pytest.mark.asyncio
async def test_family_generate_code_success(mock_config, api_mock, bot_stub, dp_module):
    """Test successful family code generation"""
    # Mock API response
    api_mock.when(
        "POST",
        "/account/users/456/family_code/",
        DummyResponse(201, {"code": "ABC123", "expires_in": 600}),
    )

    callback_query = types.SimpleNamespace(
        id="callback_123",
        data="family_generate_code",
        from_user=types.SimpleNamespace(id=456),
        message=types.SimpleNamespace(chat=types.SimpleNamespace(id=123)),
    )

    await dp_module.family_generate_code(callback_query)

    assert len(bot_stub.sent) == 1
    sent_msg = bot_stub.sent[0]
    assert sent_msg.chat_id == 123
    assert "ABC123" in sent_msg.text
    assert "10 min" in sent_msg.text
    assert "Share this with the person" in sent_msg.text


@pytest.mark.asyncio
async def test_family_generate_code_failure(mock_config, api_mock, bot_stub, dp_module):
    """Test family code generation failure"""
    # Mock API failure
    api_mock.when(
        "POST",
        "/account/users/456/family_code/",
        DummyResponse(500, {"error": "server error"}),
    )

    callback_query = types.SimpleNamespace(
        id="callback_123",
        data="family_generate_code",
        from_user=types.SimpleNamespace(id=456),
        message=types.SimpleNamespace(chat=types.SimpleNamespace(id=123)),
    )

    await dp_module.family_generate_code(callback_query)

    assert len(bot_stub.sent) == 1
    sent_msg = bot_stub.sent[0]
    assert sent_msg.chat_id == 123
    assert "Failed to generate code" in sent_msg.text


@pytest.mark.asyncio
async def test_family_enter_code_callback(mock_config, bot_stub, dp_module):
    """Test family enter code callback sets state"""
    callback_query = types.SimpleNamespace(
        id="callback_123",
        data="family_enter_code",
        from_user=types.SimpleNamespace(id=456),
        message=types.SimpleNamespace(chat=types.SimpleNamespace(id=123)),
    )

    # Mock state management
    with patch.object(dp_module.dp, "current_state") as mock_state_getter:
        mock_state = AsyncMock()
        mock_state_getter.return_value = mock_state

        await dp_module.family_enter_code(callback_query)

        # Verify state was set
        mock_state.set_state.assert_called_once()

        assert len(bot_stub.sent) == 2  # reply_on_button + instruction
        instruction_msg = bot_stub.sent[1]
        assert instruction_msg.chat_id == 123
        assert "Send the family code" in instruction_msg.text


@pytest.mark.asyncio
async def test_family_code_entered_success(mock_config, api_mock, bot_stub, dp_module):
    """Test successful family code entry and invite creation"""
    # Mock API responses
    api_mock.when(
        "POST",
        "/account/users/family_invite/proposal/",
        DummyResponse(
            201,
            {
                "invite_id": "invite123",
                "inviter_tg_id": "456",
                "member_tg_id": "789",
                "status": "pending",
            },
        ),
    )

    message = types.SimpleNamespace(
        chat=types.SimpleNamespace(id=123),
        from_user=types.SimpleNamespace(id=456, full_name="John Doe"),
        text="ABC123",
    )

    # Mock state management
    with patch.object(dp_module.dp, "current_state") as mock_state_getter:
        mock_state = AsyncMock()
        mock_state_getter.return_value = mock_state

        await dp_module.family_code_entered(message)

        # Verify state was reset
        mock_state.reset_state.assert_called_once()

    # Should send confirmation to inviter and invite to member
    assert len(bot_stub.sent) >= 1
    confirmation_msg = bot_stub.sent[0]
    assert confirmation_msg.chat_id == 123
    assert "Invite sent" in confirmation_msg.text


@pytest.mark.asyncio
async def test_family_code_entered_invalid_code(
    mock_config, api_mock, bot_stub, dp_module
):
    """Test family code entry with invalid code"""
    # Mock API failure
    api_mock.when(
        "POST",
        "/account/users/family_invite/proposal/",
        DummyResponse(404, {"error": "invalid_or_expired_code"}),
    )

    message = types.SimpleNamespace(
        chat=types.SimpleNamespace(id=123),
        from_user=types.SimpleNamespace(id=456),
        text="INVALID",
    )

    # Mock state management
    with patch.object(dp_module.dp, "current_state") as mock_state_getter:
        mock_state = AsyncMock()
        mock_state_getter.return_value = mock_state

        await dp_module.family_code_entered(message)

    assert len(bot_stub.sent) == 1
    error_msg = bot_stub.sent[0]
    assert error_msg.chat_id == 123
    assert "Invalid or expired code" in error_msg.text


@pytest.mark.asyncio
async def test_family_code_entered_empty_code(mock_config, bot_stub, dp_module):
    """Test family code entry with empty/invalid code"""
    message = types.SimpleNamespace(
        chat=types.SimpleNamespace(id=123),
        from_user=types.SimpleNamespace(id=456),
        text="",  # Empty code
    )

    # Mock state management
    with patch.object(dp_module.dp, "current_state") as mock_state_getter:
        mock_state = AsyncMock()
        mock_state_getter.return_value = mock_state

        await dp_module.family_code_entered(message)

    assert len(bot_stub.sent) == 1
    error_msg = bot_stub.sent[0]
    assert error_msg.chat_id == 123
    assert "Invalid code" in error_msg.text


@pytest.mark.asyncio
async def test_family_decision_accept(mock_config, api_mock, bot_stub, dp_module):
    """Test accepting a family invite"""
    # Mock API response
    api_mock.when(
        "POST",
        "/account/users/family_invite/decision/",
        DummyResponse(
            200,
            {
                "invite_id": "invite123",
                "status": "accepted",
                "inviter_tg_id": "789",
                "member_tg_id": "456",
            },
        ),
    )

    callback_query = types.SimpleNamespace(
        id="callback_123",
        data="family_accept_invite123",
        from_user=types.SimpleNamespace(id=456),
        message=types.SimpleNamespace(
            chat=types.SimpleNamespace(id=123), message_id=999
        ),
    )

    await dp_module.family_decision(callback_query)

    # Should send confirmation to member
    assert len(bot_stub.sent) >= 1
    confirmation_msg = bot_stub.sent[0]
    assert confirmation_msg.chat_id == 123
    assert "Family link established" in confirmation_msg.text

    # Verify buttons were removed
    assert len(bot_stub.edited_markups) == 1
    edited = bot_stub.edited_markups[0]
    assert edited.chat_id == 123
    assert edited.message_id == 999
    assert edited.reply_markup is None


@pytest.mark.asyncio
async def test_family_decision_decline(mock_config, api_mock, bot_stub, dp_module):
    """Test declining a family invite"""
    # Mock API response
    api_mock.when(
        "POST",
        "/account/users/family_invite/decision/",
        DummyResponse(
            200,
            {
                "invite_id": "invite123",
                "status": "declined",
                "inviter_tg_id": "789",
                "member_tg_id": "456",
            },
        ),
    )

    callback_query = types.SimpleNamespace(
        id="callback_123",
        data="family_decline_invite123",
        from_user=types.SimpleNamespace(id=456),
        message=types.SimpleNamespace(
            chat=types.SimpleNamespace(id=123), message_id=999
        ),
    )

    await dp_module.family_decision(callback_query)

    # Should send decline confirmation to member
    assert len(bot_stub.sent) >= 1
    confirmation_msg = bot_stub.sent[0]
    assert confirmation_msg.chat_id == 123
    assert "Invite declined" in confirmation_msg.text

    # Verify buttons were removed
    assert len(bot_stub.edited_markups) == 1
    edited = bot_stub.edited_markups[0]
    assert edited.chat_id == 123
    assert edited.message_id == 999
    assert edited.reply_markup is None


@pytest.mark.asyncio
async def test_family_decision_api_failure(mock_config, api_mock, bot_stub, dp_module):
    """Test family decision with API failure"""
    # Mock API failure
    api_mock.when(
        "POST",
        "/account/users/family_invite/decision/",
        DummyResponse(500, {"error": "server error"}),
    )

    callback_query = types.SimpleNamespace(
        id="callback_123",
        data="family_accept_invite123",
        from_user=types.SimpleNamespace(id=456),
        message=types.SimpleNamespace(
            chat=types.SimpleNamespace(id=123), message_id=999
        ),
    )

    await dp_module.family_decision(callback_query)

    # Should send error message
    assert len(bot_stub.sent) == 1
    error_msg = bot_stub.sent[0]
    assert error_msg.chat_id == 123
    assert "Failed to process decision" in error_msg.text

    # Buttons should still be removed to prevent retry
    assert len(bot_stub.edited_markups) == 1


@pytest.mark.asyncio
async def test_family_code_entered_bad_request(
    mock_config, api_mock, bot_stub, dp_module
):
    """Test family code entry with bad request response"""
    # Mock API bad request
    api_mock.when(
        "POST",
        "/account/users/family_invite/proposal/",
        DummyResponse(400, {"error": "bad request"}),
    )

    message = types.SimpleNamespace(
        chat=types.SimpleNamespace(id=123),
        from_user=types.SimpleNamespace(id=456),
        text="BADCODE",
    )

    # Mock state management
    with patch.object(dp_module.dp, "current_state") as mock_state_getter:
        mock_state = AsyncMock()
        mock_state_getter.return_value = mock_state

        await dp_module.family_code_entered(message)

    assert len(bot_stub.sent) == 1
    error_msg = bot_stub.sent[0]
    assert error_msg.chat_id == 123
    assert "Bad request" in error_msg.text


@pytest.mark.asyncio
async def test_family_code_entered_member_notification_failure(
    mock_config, api_mock, bot_stub, dp_module
):
    """Test that invite still works even if member notification fails"""
    # Mock successful API response
    api_mock.when(
        "POST",
        "/account/users/family_invite/proposal/",
        DummyResponse(
            201,
            {
                "invite_id": "invite123",
                "inviter_tg_id": "456",
                "member_tg_id": "789",
                "status": "pending",
            },
        ),
    )

    message = types.SimpleNamespace(
        chat=types.SimpleNamespace(id=123),
        from_user=types.SimpleNamespace(id=456, full_name="John Doe"),
        text="ABC123",
    )

    # Mock state management
    with patch.object(dp_module.dp, "current_state") as mock_state_getter:
        mock_state = AsyncMock()
        mock_state_getter.return_value = mock_state

        # Mock bot.send_message to fail on member notification
        original_send = bot_stub.send_message

        def selective_fail(*args, **kwargs):
            if args[0] == 789:  # member_tg_id
                raise Exception("Cannot send to user")
            return original_send(*args, **kwargs)

        bot_stub.send_message = selective_fail

        await dp_module.family_code_entered(message)

    # Should still send confirmation to inviter
    assert len(bot_stub.sent) >= 1
    confirmation_msg = bot_stub.sent[0]
    assert confirmation_msg.chat_id == 123
    assert "Invite sent" in confirmation_msg.text


@pytest.mark.asyncio
async def test_family_decision_inviter_notification_failure(
    mock_config, api_mock, bot_stub, dp_module
):
    """Test that decision still works even if inviter notification fails"""
    # Mock API response
    api_mock.when(
        "POST",
        "/account/users/family_invite/decision/",
        DummyResponse(
            200,
            {
                "invite_id": "invite123",
                "status": "accepted",
                "inviter_tg_id": "789",
                "member_tg_id": "456",
            },
        ),
    )

    callback_query = types.SimpleNamespace(
        id="callback_123",
        data="family_accept_invite123",
        from_user=types.SimpleNamespace(id=456),
        message=types.SimpleNamespace(
            chat=types.SimpleNamespace(id=123), message_id=999
        ),
    )

    # Mock bot.send_message to fail on inviter notification
    original_send = bot_stub.send_message

    def selective_fail(*args, **kwargs):
        if args[0] == 789:  # inviter_tg_id
            raise Exception("Cannot send to user")
        return original_send(*args, **kwargs)

    bot_stub.send_message = selective_fail

    await dp_module.family_decision(callback_query)

    # Should still send confirmation to member
    assert len(bot_stub.sent) >= 1
    confirmation_msg = bot_stub.sent[0]
    assert confirmation_msg.chat_id == 123
    assert "Family link established" in confirmation_msg.text


@pytest.mark.asyncio
async def test_help_command_includes_family_option(
    mock_config, api_mock, bot_stub, dp_module
):
    """Test that /help includes family option when user has account"""
    # Mock API response with matching user
    api_mock.when(
        "GET", "/monobank/monoaccounts/", DummyResponse(200, [{"user": "456"}])
    )

    message = types.SimpleNamespace(
        chat=types.SimpleNamespace(id=123),
        from_user=types.SimpleNamespace(id=456),
    )

    await dp_module.help(message)

    assert len(bot_stub.sent) == 1
    sent_msg = bot_stub.sent[0]
    assert "/family - manage family members" in sent_msg.text
