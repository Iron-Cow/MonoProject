from random import randint
from string import ascii_letters, digits

SYMBOLS = ascii_letters + digits


def generate_password(pass_lenght: int) -> str:
    password = ""
    for i in range(pass_lenght):
        password += SYMBOLS[randint(0, len(SYMBOLS) - 1)]
    return password


if __name__ == "__main__":
    print(generate_password(8))
    print(generate_password(16))
    print(generate_password(20))
