from aiogram.dispatcher.filters.state import State, StatesGroup


class MonotokenStates(StatesGroup):
    token_enter = State()
    # token_change = State()
    # token_delete = State()


class FamilyStates(StatesGroup):
    code_enter = State()


if __name__ == "__main__":
    print(MonotokenStates.token_enter)
