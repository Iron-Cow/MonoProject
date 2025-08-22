import asyncio
import types
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from .testsupport import DummyResponse


@pytest.mark.asyncio
async def test_jar_chart_options_shows_period_choices(
    mock_config, api_mock, bot_stub, dp_module
):
    """Test jar chart options callback shows time period choices"""
    # Mock jar details with complete data
    jar_data = {
        "id": "jar123",
        "title": "My Jar",
        "send_id": "send123",
        "currency": {"code": 980, "name": "UAH", "flag": "🇺🇦", "symbol": "₴"},
        "balance": 5000,
        "goal": 10000,
        "owner_name": "Test User",
        "is_budget": False,
    }
    api_mock.when("GET", "/monobank/monojars/jar123/", DummyResponse(200, jar_data))

    callback_query = types.SimpleNamespace(
        id="cb1",
        data="jar_chart_jar123",
        from_user=types.SimpleNamespace(id=456),
        message=types.SimpleNamespace(
            chat=types.SimpleNamespace(id=123), delete_reply_markup=AsyncMock()
        ),
    )

    await dp_module.jar_chart_options_handler(callback_query)

    # Should send 2 messages: reply_on_button + period selection
    assert len(bot_stub.sent) >= 1
    # The last message should be the period selection
    sent_msg = bot_stub.sent[-1]
    assert "Pick period" in sent_msg.text
    assert "My Jar" in sent_msg.text
    assert sent_msg.reply_markup is not None


@pytest.mark.asyncio
async def test_jar_chart_fetch_generates_chart_1_month(
    mock_config, api_mock, bot_stub, dp_module
):
    """Test jar chart generation for 1 month period"""
    # Mock transaction data
    transaction_data = [
        {"balance": 10000, "formatted_time": "2023-11-01 10:00:00"},
        {"balance": 15000, "formatted_time": "2023-11-15 14:30:00"},
        {"balance": 12000, "formatted_time": "2023-11-30 16:45:00"},
    ]

    # Mock jar details
    jar_data = {
        "id": "jar123",
        "title": "My Savings",
        "currency": {"name": "UAH", "symbol": "₴"},
    }

    # Mock the time calculation to return a fixed date
    api_mock.when(
        "GET",
        "/monobank/monojartransactions/?jars=jar123&fields=balance,formatted_time&time_from=2023-10-01",
        DummyResponse(200, transaction_data),
    )
    api_mock.when("GET", "/monobank/monojars/jar123/", DummyResponse(200, jar_data))

    callback_query = types.SimpleNamespace(
        id="cb1",
        data="jar_chart_period_jar123*1m",
        message=types.SimpleNamespace(chat=types.SimpleNamespace(id=123)),
    )

    # Mock matplotlib and InputFile to avoid actual chart generation
    with patch("src.bot._compute_time_from", return_value="2023-10-01"), patch(
        "src.bot.plt"
    ) as mock_plt, patch("src.bot.io.BytesIO") as mock_bytesio, patch(
        "src.bot.InputFile"
    ) as mock_inputfile:

        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)
        mock_buf = MagicMock()
        mock_bytesio.return_value = mock_buf
        mock_inputfile.return_value = MagicMock()

        await dp_module.jar_chart_fetch_handler(callback_query)

    # Should send photo with chart
    assert len(bot_stub.sent) == 1
    sent_msg = bot_stub.sent[0]
    assert sent_msg.photo is not None
    assert "1 month" in sent_msg.caption


@pytest.mark.asyncio
async def test_jar_chart_fetch_handles_no_data(
    mock_config, api_mock, bot_stub, dp_module
):
    """Test jar chart generation when no transaction data available"""
    # Mock empty transaction data - return 200 with empty list for proper handling
    api_mock.when(
        "GET",
        "/monobank/monojartransactions/?jars=jar123&fields=balance,formatted_time&time_from=2023-10-01",
        DummyResponse(200, []),
    )

    callback_query = types.SimpleNamespace(
        id="cb1",
        data="jar_chart_period_jar123*1m",
        message=types.SimpleNamespace(chat=types.SimpleNamespace(id=123)),
    )

    with patch("src.bot._compute_time_from", return_value="2023-10-01"):
        await dp_module.jar_chart_fetch_handler(callback_query)

    assert len(bot_stub.sent) == 1
    sent_msg = bot_stub.sent[0]
    assert "No transactions to display" in sent_msg.text


@pytest.mark.asyncio
async def test_jar_chart_fetch_handles_api_error(
    mock_config, api_mock, bot_stub, dp_module
):
    """Test jar chart generation when API returns error"""
    # Mock API error
    api_mock.when(
        "GET",
        "/monobank/monojartransactions/?jars=jar123&fields=balance,formatted_time&time_from=2023-10-01",
        DummyResponse(500, None, "Server error"),
    )

    callback_query = types.SimpleNamespace(
        id="cb1",
        data="jar_chart_period_jar123*1m",
        message=types.SimpleNamespace(chat=types.SimpleNamespace(id=123)),
    )

    with patch("src.bot._compute_time_from", return_value="2023-10-01"):
        await dp_module.jar_chart_fetch_handler(callback_query)

    assert len(bot_stub.sent) == 1
    sent_msg = bot_stub.sent[0]
    assert "Failed to fetch transactions" in sent_msg.text
    assert "500" in sent_msg.text


@pytest.mark.asyncio
async def test_jar_chart_fetch_all_time_period(
    mock_config, api_mock, bot_stub, dp_module
):
    """Test jar chart generation for all time period (no time filter)"""
    # Mock transaction data
    transaction_data = [
        {"balance": 5000, "formatted_time": "2022-01-01 10:00:00"},
        {"balance": 25000, "formatted_time": "2023-06-15 14:30:00"},
        {"balance": 30000, "formatted_time": "2023-11-30 16:45:00"},
    ]

    jar_data = {
        "id": "jar123",
        "title": "Long Term Savings",
        "currency": {"name": "UAH", "symbol": "₴"},
    }

    # For "all" period, no time_from parameter should be added
    api_mock.when(
        "GET",
        "/monobank/monojartransactions/?jars=jar123&fields=balance,formatted_time",
        DummyResponse(200, transaction_data),
    )
    api_mock.when("GET", "/monobank/monojars/jar123/", DummyResponse(200, jar_data))

    callback_query = types.SimpleNamespace(
        id="cb1",
        data="jar_chart_period_jar123*all",
        message=types.SimpleNamespace(chat=types.SimpleNamespace(id=123)),
    )

    with patch("src.bot.plt") as mock_plt, patch(
        "src.bot.io.BytesIO"
    ) as mock_bytesio, patch("src.bot.InputFile") as mock_inputfile:

        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)
        mock_buf = MagicMock()
        mock_bytesio.return_value = mock_buf
        mock_inputfile.return_value = MagicMock()

        await dp_module.jar_chart_fetch_handler(callback_query)

    assert len(bot_stub.sent) == 1
    sent_msg = bot_stub.sent[0]
    assert sent_msg.photo is not None
    assert "All time" in sent_msg.caption


@pytest.mark.asyncio
async def test_jar_chart_fetch_3_months_period(
    mock_config, api_mock, bot_stub, dp_module
):
    """Test jar chart generation for 3 months period"""
    # Mock transaction data
    transaction_data = [
        {"balance": 8000, "formatted_time": "2023-09-01 10:00:00"},
        {"balance": 18000, "formatted_time": "2023-10-15 14:30:00"},
        {"balance": 22000, "formatted_time": "2023-11-30 16:45:00"},
    ]

    jar_data = {
        "id": "jar123",
        "title": "Quarterly Jar",
        "currency": {"name": "EUR", "symbol": "€"},
    }

    api_mock.when(
        "GET",
        "/monobank/monojartransactions/?jars=jar123&fields=balance,formatted_time&time_from=2023-08-01",
        DummyResponse(200, transaction_data),
    )
    api_mock.when("GET", "/monobank/monojars/jar123/", DummyResponse(200, jar_data))

    callback_query = types.SimpleNamespace(
        id="cb1",
        data="jar_chart_period_jar123*3m",
        message=types.SimpleNamespace(chat=types.SimpleNamespace(id=123)),
    )

    with patch("src.bot._compute_time_from", return_value="2023-08-01"), patch(
        "src.bot.plt"
    ) as mock_plt, patch("src.bot.io.BytesIO") as mock_bytesio, patch(
        "src.bot.InputFile"
    ) as mock_inputfile:

        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)
        mock_buf = MagicMock()
        mock_bytesio.return_value = mock_buf
        mock_inputfile.return_value = MagicMock()

        await dp_module.jar_chart_fetch_handler(callback_query)

    assert len(bot_stub.sent) == 1
    sent_msg = bot_stub.sent[0]
    assert sent_msg.photo is not None
    assert "3 months" in sent_msg.caption


def test_compute_time_from_helper():
    """Test _compute_time_from helper function for different periods"""
    from src.bot import _compute_time_from

    # Test 1 month
    result_1m = _compute_time_from("1m")
    assert result_1m is not None
    assert len(result_1m) == 10  # YYYY-MM-DD format

    # Test 3 months
    result_3m = _compute_time_from("3m")
    assert result_3m is not None
    assert len(result_3m) == 10

    # Test all time (should return None)
    result_all = _compute_time_from("all")
    assert result_all is None

    # Test unknown period
    result_unknown = _compute_time_from("unknown")
    assert result_unknown is None
