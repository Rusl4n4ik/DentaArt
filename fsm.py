from enum import auto

from aiogram.dispatcher.filters.state import StatesGroup, State


class Users(StatesGroup):
    Name = State()
    Phnum = State()


class Admins(StatesGroup):
    Broadcast = State()
    AddServicePrice = State()
    AddServiceName = State()
    EditPriceAmount = State()
    EditPriceList = State()
    EditService = State()


class Update(StatesGroup):
    Name = State()
    Phnum = State()


class Appointment(StatesGroup):
    CURRENT_TIME = State()
    SET_REASON = State()
    SET_DAY = State()
    SET_HOUR_CHOOSE = State()
    SET_HOUR = State()
    SET_MONTH = State()
    CURRENT_MONTH = State()
    CONFIRM = State()
    SET_TIME = State()
    SET_DATE = State()


