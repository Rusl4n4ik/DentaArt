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
    EditServiceName = State()
    EditPriceList = State()
    EditService = State()
    BroadcastTextAppointments = State()
    BroadcastTextAll = State()
    CalendarM = State()
    CalendarH = State()
    ViewHour = State()
    HOUR_CHOOSE = State()
    ViewDay = State()
    SET_REASON = State()
    SET_DAY = State()
    SET_HOUR_CHOOSE = State()
    SET_HOUR = State()
    SET_MONTH = State()


class Update(StatesGroup):
    Name = State()
    Phnum = State()


class Appointments(StatesGroup):
    CURRENT_TIME = State()
    SET_REASON = State()
    SET_REASON_CONFIRM = State()
    SET_DAY = State()
    SET_HOUR_CHOOSE = State()
    SET_HOUR = State()
    SET_MONTH = State()
    CURRENT_MONTH = State()
    CONFIRM = State()
    DAY = State()
    SET_TIME = State()
    SET_DATE = State()
    DELETE_CONFIRM = State()
    CANCEL_CONFIRM = State()
    DELETE_REASON = State()
    ENTER_PHONE_OFF = State()
    ENTER_NAME_OFF = State()


class Offline(StatesGroup):
    Name = State()
    Phnum = State()
    SET_REASON = State()
    SET_DAY = State()
    SET_HOUR_CHOOSE = State()
    SET_HOUR = State()
    SET_MONTH = State()
