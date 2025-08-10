from random import randint
from string import ascii_letters, digits

from datadict import dataclass


@dataclass(order=True)
class CurrencyInfo:
    code: int
    name: str
    flag: str
    symbol: str


@dataclass(order=True)
class MonoJar:
    id: str
    send_id: str
    title: str
    currency: CurrencyInfo
    balance: int
    goal: int
    owner_name: str
    is_budget: bool


SYMBOLS = ascii_letters + digits


def generate_password(pass_lenght: int) -> str:
    password = ""
    for i in range(pass_lenght):
        password += SYMBOLS[randint(0, len(SYMBOLS) - 1)]
    return password


def get_jar_data(jar_data: dict) -> MonoJar:
    currency = CurrencyInfo(**jar_data.get("currency", {}))
    jar_data.pop("currency")
    jar_obj = MonoJar(**jar_data, currency=currency)  # pyright: ignore[reportCallIssue]
    return jar_obj


if __name__ == "__main__":
    print(generate_password(8))
    print(generate_password(16))
    print(generate_password(20))
