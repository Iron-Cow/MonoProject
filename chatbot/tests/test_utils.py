from src.utils import MonoJar, generate_password, get_jar_data


def test_generate_password_length_and_charset():
    pwd = generate_password(16)
    assert isinstance(pwd, str)
    assert len(pwd) == 16
    # Only ascii letters and digits
    for ch in pwd:
        assert ch.isalnum()


def test_get_jar_data_parses_currency_and_jar():
    jar_input = {
        "id": "jar123",
        "send_id": "send123",
        "title": "My Jar",
        "currency": {
            "code": 980,
            "name": "UAH",
            "flag": "🇺🇦",
            "symbol": "₴",
        },
        "balance": 12345,
        "goal": 50000,
        "owner_name": "User",
        "is_budget": True,
    }

    jar = get_jar_data(jar_input.copy())
    assert isinstance(jar, MonoJar)
    assert jar.id == "jar123"
    assert jar.currency.name == "UAH"
    assert jar.currency.symbol == "₴"
    assert jar.is_budget is True
