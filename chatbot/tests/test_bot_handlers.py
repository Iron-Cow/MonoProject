import asyncio
import types
from unittest.mock import AsyncMock, MagicMock

import pytest

from .testsupport import DummyResponse


@pytest.mark.asyncio
async def test_start_command_sends_welcome_message(mock_config, bot_stub, dp_module):
    """Test /start command sends welcome message"""
    message = types.SimpleNamespace(
        chat=types.SimpleNamespace(id=123),
        from_user=types.SimpleNamespace(id=456),
    )

    await dp_module.start(message)

    assert len(bot_stub.sent) == 1
    sent_msg = bot_stub.sent[0]
    assert sent_msg.chat_id == 123
    assert "Hi, my young monouser" in sent_msg.text
    assert "/help" in sent_msg.text
    assert "/register" in sent_msg.text


@pytest.mark.asyncio
async def test_help_command_shows_register_when_no_account(
    mock_config, api_mock, bot_stub, dp_module
):
    """Test /help shows register option when user has no account"""
    # Mock API response with no matching user
    api_mock.when(
        "GET", "/monobank/monoaccounts/", DummyResponse(200, [{"user": "999"}])
    )

    message = types.SimpleNamespace(
        chat=types.SimpleNamespace(id=123),
        from_user=types.SimpleNamespace(id=456),
    )

    await dp_module.help(message)

    assert len(bot_stub.sent) == 1
    sent_msg = bot_stub.sent[0]
    assert "/register" in sent_msg.text
    assert "/help" in sent_msg.text


@pytest.mark.asyncio
async def test_help_command_shows_advanced_options_with_account(
    mock_config, api_mock, bot_stub, dp_module
):
    """Test /help shows monojars and daily report when user has account"""
    # Mock API response with matching user
    api_mock.when(
        "GET",
        "/monobank/monoaccounts/",
        DummyResponse(200, [{"user": "456", "active": True}]),
    )

    message = types.SimpleNamespace(
        chat=types.SimpleNamespace(id=123),
        from_user=types.SimpleNamespace(id=456),
    )

    await dp_module.help(message)

    assert len(bot_stub.sent) == 1
    sent_msg = bot_stub.sent[0]
    assert "/monojars" in sent_msg.text
    assert "/daily_report" in sent_msg.text


@pytest.mark.asyncio
async def test_register_command_shows_button_for_new_user(
    mock_config, api_mock, bot_stub, dp_module
):
    """Test /register shows registration button for new user"""
    # Mock API response - user not found (404)
    api_mock.when("GET", "/account/users/456", DummyResponse(404, None, "Not found"))

    message = types.SimpleNamespace(
        chat=types.SimpleNamespace(id=123),
        from_user=types.SimpleNamespace(id=456),
    )

    await dp_module.register(message)

    assert len(bot_stub.sent) == 1
    sent_msg = bot_stub.sent[0]
    assert "create account" in sent_msg.text
    assert sent_msg.reply_markup is not None


@pytest.mark.asyncio
async def test_register_command_rejects_existing_user(
    mock_config, api_mock, bot_stub, dp_module
):
    """Test /register rejects already registered user"""
    # Mock API response - user exists
    api_mock.when("GET", "/account/users/456", DummyResponse(200, {"id": 456}))

    message = types.SimpleNamespace(
        chat=types.SimpleNamespace(id=123),
        from_user=types.SimpleNamespace(id=456),
    )

    await dp_module.register(message)

    assert len(bot_stub.sent) == 1
    sent_msg = bot_stub.sent[0]
    assert "registered already" in sent_msg.text


@pytest.mark.asyncio
async def test_register_monouser_callback_creates_account(
    mock_config, api_mock, bot_stub, dp_module
):
    """Test register callback creates user account with generated password"""
    # Mock successful user creation
    api_mock.when("POST", "/account/users/", DummyResponse(201, {"id": 456}))

    callback_query = types.SimpleNamespace(
        id="cb1",
        data="register_monouser",
        from_user=types.SimpleNamespace(id=456, first_name="John", last_name="Doe"),
        message=types.SimpleNamespace(
            chat=types.SimpleNamespace(id=123), delete_reply_markup=AsyncMock()
        ),
    )

    await dp_module.register_monouser(callback_query)

    # Should send multiple messages: login, name, password, next steps
    assert len(bot_stub.sent) >= 4
    # Check that password message contains spoiler tags
    password_msg = next(
        (msg for msg in bot_stub.sent if "||" in (msg.text or "")), None
    )
    assert password_msg is not None
    # Check final instruction about token
    assert any("token" in (msg.text or "") for msg in bot_stub.sent)


@pytest.mark.asyncio
async def test_monojars_command_shows_options(mock_config, bot_stub, dp_module):
    """Test /monojars command shows jar options"""
    message = types.SimpleNamespace(
        chat=types.SimpleNamespace(id=123),
        from_user=types.SimpleNamespace(id=456),
    )

    await dp_module.monojars(message)

    assert len(bot_stub.sent) == 1
    sent_msg = bot_stub.sent[0]
    assert sent_msg.reply_markup is not None
    assert "pick your option" in sent_msg.text


@pytest.mark.asyncio
async def test_get_user_jars_displays_jar_info(
    mock_config, api_mock, bot_stub, dp_module
):
    """Test get_user_jars callback displays jar information"""
    # Mock jar data
    jar_data = [
        {
            "id": "jar123",
            "send_id": "send123",
            "title": "My Savings",
            "currency": {"code": 980, "name": "UAH", "flag": "🇺🇦", "symbol": "₴"},
            "balance": 15000,
            "goal": 50000,
            "owner_name": "John Doe",
            "is_budget": False,
        }
    ]
    api_mock.when("GET", "/monobank/monojars/?users=456", DummyResponse(200, jar_data))

    callback_query = types.SimpleNamespace(
        id="cb1",
        data="get_user_jars",
        from_user=types.SimpleNamespace(id=456),
        message=types.SimpleNamespace(
            chat=types.SimpleNamespace(id=123), delete_reply_markup=AsyncMock()
        ),
    )

    await dp_module.get_user_jars_combined(callback_query)

    # Should send jar info message
    assert len(bot_stub.sent) >= 1
    jar_msg = bot_stub.sent[-1]
    assert "My Savings" in jar_msg.text
    assert "UAH" in jar_msg.text
    assert "John Doe" in jar_msg.text


@pytest.mark.asyncio
async def test_get_user_jars_handles_empty_response(
    mock_config, api_mock, bot_stub, dp_module
):
    """Test get_user_jars handles empty jar list"""
    api_mock.when("GET", "/monobank/monojars/?users=456", DummyResponse(200, []))

    callback_query = types.SimpleNamespace(
        id="cb1",
        data="get_user_jars",
        from_user=types.SimpleNamespace(id=456),
        message=types.SimpleNamespace(
            chat=types.SimpleNamespace(id=123), delete_reply_markup=AsyncMock()
        ),
    )

    await dp_module.get_user_jars_combined(callback_query)

    assert len(bot_stub.sent) >= 1
    sent_msg = bot_stub.sent[-1]
    assert "No jars to display" in sent_msg.text


@pytest.mark.asyncio
async def test_daily_report_command_shows_management_options(
    mock_config, bot_stub, dp_module
):
    """Test /daily_report shows enable/disable options"""
    message = types.SimpleNamespace(
        chat=types.SimpleNamespace(id=123),
        from_user=types.SimpleNamespace(id=456),
    )

    await dp_module.daily_report(message)

    assert len(bot_stub.sent) == 1
    sent_msg = bot_stub.sent[0]
    assert "Daily Transaction Report" in sent_msg.text
    assert "21:00" in sent_msg.text
    assert sent_msg.reply_markup is not None


@pytest.mark.asyncio
async def test_enable_daily_report_success(mock_config, api_mock, bot_stub, dp_module):
    """Test enable daily report callback with successful API response"""
    api_mock.when("POST", "/monobank/daily-report-scheduler/", DummyResponse(201, {}))

    callback_query = types.SimpleNamespace(
        id="cb1",
        data="enable_daily_report_456",
        message=types.SimpleNamespace(chat=types.SimpleNamespace(id=123)),
    )

    await dp_module.enable_daily_report_handler(callback_query)

    assert len(bot_stub.sent) == 1
    sent_msg = bot_stub.sent[0]
    assert "Daily Report Enabled" in sent_msg.text
    assert "21:00" in sent_msg.text


@pytest.mark.asyncio
async def test_enable_daily_report_failure(mock_config, api_mock, bot_stub, dp_module):
    """Test enable daily report callback with API failure"""
    api_mock.when(
        "POST",
        "/monobank/daily-report-scheduler/",
        DummyResponse(500, None, "Server error"),
    )

    callback_query = types.SimpleNamespace(
        id="cb1",
        data="enable_daily_report_456",
        message=types.SimpleNamespace(chat=types.SimpleNamespace(id=123)),
    )

    await dp_module.enable_daily_report_handler(callback_query)

    assert len(bot_stub.sent) == 1
    sent_msg = bot_stub.sent[0]
    assert "Failed to enable" in sent_msg.text
    assert "500" in sent_msg.text


@pytest.mark.asyncio
async def test_disable_daily_report_success(mock_config, api_mock, bot_stub, dp_module):
    """Test disable daily report callback with successful API response"""
    api_mock.when("DELETE", "/monobank/daily-report-scheduler/", DummyResponse(200, {}))

    callback_query = types.SimpleNamespace(
        id="cb1",
        data="disable_daily_report_456",
        message=types.SimpleNamespace(chat=types.SimpleNamespace(id=123)),
    )

    await dp_module.disable_daily_report_handler(callback_query)

    assert len(bot_stub.sent) == 1
    sent_msg = bot_stub.sent[0]
    assert "Daily Report Disabled" in sent_msg.text


@pytest.mark.asyncio
async def test_disable_daily_report_not_found(
    mock_config, api_mock, bot_stub, dp_module
):
    """Test disable daily report when no active report exists"""
    api_mock.when(
        "DELETE",
        "/monobank/daily-report-scheduler/",
        DummyResponse(404, None, "Not found"),
    )

    callback_query = types.SimpleNamespace(
        id="cb1",
        data="disable_daily_report_456",
        message=types.SimpleNamespace(chat=types.SimpleNamespace(id=123)),
    )

    await dp_module.disable_daily_report_handler(callback_query)

    assert len(bot_stub.sent) == 1
    sent_msg = bot_stub.sent[0]
    assert "No Active Daily Report" in sent_msg.text


@pytest.mark.asyncio
async def test_toggle_budget_jar_success(mock_config, api_mock, bot_stub, dp_module):
    """Test toggle budget jar callback with successful API response"""
    api_mock.when(
        "PATCH", "/monobank/monojars/jar123/set_budget_status/", DummyResponse(200, {})
    )

    callback_query = types.SimpleNamespace(
        id="cb1",
        data="toggle_budget_jar123*0",  # current_flag=0, so will set to 1
        message=types.SimpleNamespace(
            chat=types.SimpleNamespace(id=123), message_id=456
        ),
    )

    await dp_module.toggle_budget_handler(callback_query)

    # Should edit message markup and answer callback
    assert len(bot_stub.edited_markups) == 1
    assert len(bot_stub.answered_callbacks) == 1
    assert "Set as budget ✅" in bot_stub.answered_callbacks[0][1]


@pytest.mark.asyncio
async def test_jar_available_months_displays_months(
    mock_config, api_mock, bot_stub, dp_module
):
    """Test jar available months callback displays month options"""
    # Mock jar details and available months
    jar_data = {
        "id": "jar123",
        "title": "My Jar",
        "currency": {"code": 980, "name": "UAH", "flag": "🇺🇦", "symbol": "₴"},
        "send_id": "send123",
        "balance": 5000,
        "goal": 10000,
        "owner_name": "Test User",
        "is_budget": False,
    }
    months = ["2023-11-01", "2023-12-01", "2024-01-01"]

    api_mock.when("GET", "/monobank/monojars/jar123/", DummyResponse(200, jar_data))
    api_mock.when(
        "GET", "/monobank/monojars/jar123/available-months/", DummyResponse(200, months)
    )

    callback_query = types.SimpleNamespace(
        id="cb1",
        data="jar_months_jar123",
        message=types.SimpleNamespace(chat=types.SimpleNamespace(id=123)),
    )

    await dp_module.jar_available_months_handler(callback_query)

    assert len(bot_stub.sent) == 1
    sent_msg = bot_stub.sent[0]
    assert "My Jar" in sent_msg.text
    assert "Pick month" in sent_msg.text
    assert sent_msg.reply_markup is not None


@pytest.mark.asyncio
async def test_jar_month_summary_displays_summary(
    mock_config, api_mock, bot_stub, dp_module
):
    """Test jar month summary callback displays financial summary"""
    # Mock jar and summary data
    jar_data = {
        "id": "jar123",
        "title": "My Jar",
        "currency": {"code": 980, "name": "UAH", "flag": "🇺🇦", "symbol": "₴"},
        "send_id": "send123",
        "balance": 12000,
        "goal": 20000,
        "owner_name": "Test User",
        "is_budget": False,
    }
    summary_data = {
        "start_balance": 10000,
        "budget": 5000,
        "end_balance": 12000,
        "spent": 3000,
    }

    api_mock.when("GET", "/monobank/monojars/jar123/", DummyResponse(200, jar_data))
    api_mock.when(
        "GET",
        "/monobank/monojars/jar123/month-summary/?month=2023-11-01",
        DummyResponse(200, summary_data),
    )

    callback_query = types.SimpleNamespace(
        id="cb1",
        data="jar_month_summary_jar123*2023-11-01",
        message=types.SimpleNamespace(chat=types.SimpleNamespace(id=123)),
    )

    await dp_module.jar_month_summary_handler(callback_query)

    assert len(bot_stub.sent) == 1
    sent_msg = bot_stub.sent[0]
    assert "My Jar" in sent_msg.text
    assert "2023-11" in sent_msg.text
    assert "100.00" in sent_msg.text  # start_balance/100
    assert "50.00" in sent_msg.text  # budget/100


@pytest.mark.asyncio
async def test_token_add_command_shows_instructions(mock_config, bot_stub, dp_module):
    """Test /token_add command shows token instructions"""
    message = types.SimpleNamespace(
        chat=types.SimpleNamespace(id=123),
        from_user=types.SimpleNamespace(id=456),
    )

    await dp_module.token_add(message)

    assert len(bot_stub.sent) == 1
    sent_msg = bot_stub.sent[0]
    assert "monobank token" in sent_msg.text
    assert "read\\-only permissions" in sent_msg.text  # Text is escaped for markdown
    assert sent_msg.reply_markup is not None


@pytest.mark.asyncio
async def test_add_monotoken_callback_sets_state(
    mock_config, api_mock, bot_stub, dp_module, monkeypatch
):
    """Test add mono token callback sets FSM state"""
    # Mock the state setting mechanism
    mock_state = AsyncMock()
    mock_current_state = MagicMock(return_value=mock_state)
    monkeypatch.setattr(dp_module.dp, "current_state", mock_current_state)

    callback_query = types.SimpleNamespace(
        id="cb1",
        data="add_mono_token",
        from_user=types.SimpleNamespace(id=456),
        message=types.SimpleNamespace(
            chat=types.SimpleNamespace(id=123), delete_reply_markup=AsyncMock()
        ),
    )

    await dp_module.add_monotoken(callback_query)

    # Should set FSM state and send instructions
    mock_state.set_state.assert_called_once()
    assert len(bot_stub.sent) >= 1
    assert any("Send your token" in (msg.text or "") for msg in bot_stub.sent)


@pytest.mark.asyncio
async def test_token_message_handler_saves_token(
    mock_config, api_mock, bot_stub, dp_module, monkeypatch
):
    """Test token message handler saves mono token"""
    # Mock successful token save
    api_mock.when("POST", "/monobank/monoaccounts/", DummyResponse(201, {"id": 1}))

    # Mock state reset
    mock_state = AsyncMock()
    mock_current_state = MagicMock(return_value=mock_state)
    monkeypatch.setattr(dp_module.dp, "current_state", mock_current_state)

    message = types.SimpleNamespace(
        chat=types.SimpleNamespace(id=123),
        from_user=types.SimpleNamespace(id=456),
        text="uSomeMonoTokenHere123",
    )

    await dp_module.token(message)

    # Should reset state and confirm success
    mock_state.reset_state.assert_called_once()
    assert len(bot_stub.sent) == 1
    sent_msg = bot_stub.sent[0]
    assert "Great!" in sent_msg.text
    assert "/help" in sent_msg.text


@pytest.mark.asyncio
async def test_cancel_callback_resets_state(
    mock_config, bot_stub, dp_module, monkeypatch
):
    """Test cancel callback resets FSM state"""
    # Mock state reset
    mock_state = AsyncMock()
    mock_current_state = MagicMock(return_value=mock_state)
    monkeypatch.setattr(dp_module.dp, "current_state", mock_current_state)

    callback_query = types.SimpleNamespace(
        id="cb1",
        data="cancel",
        from_user=types.SimpleNamespace(id=456),
        message=types.SimpleNamespace(
            chat=types.SimpleNamespace(id=123), delete_reply_markup=AsyncMock()
        ),
    )

    await dp_module.cancel(callback_query)

    # Should reset state
    mock_state.reset_state.assert_called_once()


@pytest.mark.asyncio
async def test_echo_handler_responds_to_unknown_message(
    mock_config, bot_stub, dp_module
):
    """Test echo handler responds to unrecognized messages"""
    message = types.SimpleNamespace(
        chat=types.SimpleNamespace(id=123),
        from_user=types.SimpleNamespace(id=456, username="testuser"),
        text="random message",
    )

    await dp_module.echo(message)

    assert len(bot_stub.sent) == 1
    sent_msg = bot_stub.sent[0]
    assert "Something unknown" in sent_msg.text
    assert "random message" in sent_msg.text
