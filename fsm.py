from aiogram.dispatcher.filters.state import StatesGroup, State


class Users(StatesGroup):
    Name = State()
    Phnum = State()


class Admins(StatesGroup):
    Broadcast = State()
    EditPrice = State()

class Update(StatesGroup):
    Name = State()
    Phnum = State()