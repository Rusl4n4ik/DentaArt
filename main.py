import asyncio
import calendar
import json
from datetime import datetime, timedelta
import keyboard
from locales import get_text
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from db import Session, Appointment
from keyboard import russian_month_names
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove, CallbackQuery, ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import db,re,keyboard
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import aiogram.utils.markdown as fmt
from fsm import Users, Update, Appointments
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger


scheduler = AsyncIOScheduler()
scheduler.start()

API_TOKEN = '6494026269:AAFptKHhMWHC2vCbUBNfNwrij-dDHANbkdw'

bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())
tmp = {}
user_languages = {}


def set_user_language(user_id, language):
    user_languages[user_id] = language


global user_language


@dp.message_handler(commands=['start'], state='*')
async def start_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_language = user_languages.get(user_id)

    exist_user = db.check_existing(message.chat.id)
    if not exist_user:
        await message.answer('👋Добро пожаловать в телеграм-бот стоматологии <b>Denta Art</b>\n <b><i>Выберите язык интерфейса:</i></b>\n➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n 👋<b>Denta Art</b> stomatologiyasi telegram- botiga xush kelibsiz\n <b><i>Interfeys tilini tanlang:</i></b>', reply_markup=keyboard.languages)

        @dp.callback_query_handler(lambda c: c.data == 'ru')
        async def process_callback_ru(callback_query: types.CallbackQuery):
            await bot.send_message(callback_query.from_user.id, get_text('ru','fill_info1'))
            set_user_language(user_id, 'ru')
            await Users.Name.set()

        @dp.callback_query_handler(lambda c: c.data == 'uz')
        async def process_callback_uz(callback_query: types.CallbackQuery):
            await bot.send_message(callback_query.from_user.id, get_text('uz', 'fill_info1'))
            set_user_language(user_id, 'uz')
            await Users.Name.set()
    else:
        await message.answer(get_text(user_language, 'greeting'), reply_markup=keyboard.get_start_keyboard(user_language))


@dp.message_handler(state=Users.Name)
async def phnum(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_language = db.get_user_language(db.session,user_id)
    name_input = message.text
    lastname_name_surname = name_input.split()
    if len(lastname_name_surname) == 3:
        lastname, name, surname = lastname_name_surname
        if re.match(r'^[А-ЯЁа-яё]+\s[А-ЯЁа-яё]+\s[А-ЯЁа-яё]+$', name_input) or re.match(r'^[A-Za-z]+\s[A-Za-z]+\s[A-Za-z]+$', name_input):
            lastname = lastname.capitalize()
            name = name.capitalize()
            surname = surname.capitalize()
            lastname_name_surname = lastname + ' ' + name + ' ' + surname
            await state.update_data(name=lastname_name_surname)
            await message.answer(get_text(user_language, 'fill_info2'))
            await Users.Phnum.set()
        else:
            await message.answer(get_text(user_language, 'fill_info_error1'))
    else:
        await message.answer(get_text('uz', 'name_update_error'))


@dp.message_handler(state=Users.Phnum)
async def addphnum(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_language = user_languages.get(user_id, 'default_language')
    phnum = message.text
    if re.match(r'^\+998\d{9}$', phnum):
        await state.update_data(phnum=phnum)
        data = await state.get_data()
        db.add_user(message.chat.id, first_name=message.from_user.first_name, username=message.from_user.username, name=data['name'], phnum=data['phnum'], language=user_language)
        await state.finish()
        await message.answer(get_text(user_language, 'greeting'), reply_markup=keyboard.get_start_keyboard(user_language))
    else:
        await message.answer(get_text(user_language, 'fill_info_error2'))


@dp.message_handler(text="🏥 О Клинике" or "🏥 Klinika haqida", state='*')
async def about(message: types.Message):
    user_id = message.from_user.id
    user_language = user_languages.get(user_id, 'default_language')
    loading_msg = await message.answer("🔄", reply_markup=types.ReplyKeyboardRemove())
    await asyncio.sleep(1)
    await bot.delete_message(chat_id=message.chat.id, message_id=loading_msg.message_id)
    await message.answer(get_text(user_language, 'info'), reply_markup=keyboard.get_back_keyboard(user_language))


@dp.message_handler(text="💵 Прайс-лист" or "💵 Narxlar ro'yxati", state='*')
async def price(message: types.Message):
    user_id = message.from_user.id
    user_language = user_languages.get(user_id, 'default_language')
    loading_msg = await message.answer('🔄', reply_markup=types.ReplyKeyboardRemove())
    await asyncio.sleep(1)
    await bot.delete_message(chat_id=message.chat.id, message_id=loading_msg.message_id)
    user_id = message.from_user.id
    user_language = user_languages.get(user_id)
    prices = db.get_all_prices(db.session)
    price_list_text = get_text(user_language, 'price_info')
    for index, price in enumerate(prices, start=1):
        price_list_text += f"{index}. <b>{price.service}:</b> {price.price}\n"
    await message.answer(price_list_text, parse_mode="HTML", reply_markup=keyboard.get_back_keyboard(user_language))


@dp.message_handler(text=("👤 Личный кабинет" or "👤 Shaxsiy kabinet"), state='*')
async def user_info(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_language = user_languages.get(user_id, 'default_language')
    async with state.proxy() as data:
        chat_id = message.chat.id
        user_id = message.from_user.id
        user_language = user_languages.get(user_id, 'default_language')
        user_info = db.get_user_info(chat_id)
        name = user_info['name']
        num = user_info['phnum']
        loading_msg = await message.answer(get_text(user_language, 'loading'), reply_markup=types.ReplyKeyboardRemove())
        await asyncio.sleep(1)
        await bot.delete_message(chat_id=message.chat.id, message_id=loading_msg.message_id)
        await message.answer(f'<b>Ваше ФИО:</b> {name}\n<b>Ваш номер телефона:</b> {num}\n'
                             '👤 В личном кабинете Вы сможете поменять данные о пациенте <b>(О себе)</b> или же просмотреть свои записи по кнопке "✏Мои записи"\n\n\n'
                             ' <b><i>Выберите пункт, который хотите поменять:</i></b>\nЕсли нечего менять, вернитесь на предыдущую страницу, используя кнопку "🔙Назад"', reply_markup=keyboard.get_user_keyboard(user_language))


@dp.callback_query_handler(lambda c: c.data == 'ch_lang', state='*')
async def change_lang(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_language = user_languages.get(user_id, 'default_language')
    await callback.message.answer(get_text(user_language, 'lang_opt'), reply_markup=keyboard.languages)


@dp.callback_query_handler(lambda c: c.data == 'back', state='*')
async def go_back(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_language = user_languages.get(user_id, 'default_language')
    current_state = await state.get_state()
    user_language = user_languages.get(callback.from_user.id, 'default_language')
    print(current_state)
    if current_state == 'Appointments:SET_HOUR_CHOOSE':
        await callback.message.delete()
        await state.reset_state()
        await start_appointment(callback.message)
    elif current_state == 'Appointments:SET_REASON':
        await choose_time(callback, state)
    elif current_state == 'Appointments:DELETE_CONFIRM':
        await show_appointments(callback, state)
    elif current_state == 'Appointments:CANCEL_CONFIRM':
        await show_appointments(callback, state)
    else:
        user_id = callback.from_user.id
        user_language = user_languages.get(user_id, 'default_language')
        await callback.message.delete()
        await state.finish()
        await callback.message.answer(get_text(user_language, 'greeting'),reply_markup=keyboard.get_start_keyboard(user_language))


@dp.callback_query_handler(lambda c: c.data == 'ch_name')
async def change_name(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_language = user_languages.get(user_id, 'default_language')
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer(get_text(user_language, 'enter_name'), reply_markup=types.ReplyKeyboardRemove())
    await Update.Name.set()


@dp.callback_query_handler(lambda c: c.data == 'ch_number')
async def change_number(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_language = user_languages.get(user_id, 'default_language')
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer(get_text(user_language, 'enter_num'), reply_markup=types.ReplyKeyboardRemove())
    await Update.Phnum.set()


@dp.message_handler(state=Update.Name)
async def set_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_language = user_languages.get(user_id, 'default_language')
    async with state.proxy() as data:
        chat_id = message.chat.id
        new_name = message.text
        if re.match(r'^[А-ЯЁа-яё]+\s[А-ЯЁа-яё]+\s[А-ЯЁа-яё]+$', new_name) or re.match(r'^[A-Za-z]+\s[A-Za-z]+\s[A-Za-z]+$', new_name):
            old_data = await state.get_data()
            db.update_user(chat_id, name=new_name, phnum=old_data.get('phnum'))
            await state.finish()
            await message.answer(get_text(user_language, 'name_update'), reply_markup=keyboard.get_back_keyboard(user_language))
        else:
            await message.answer(get_text(user_language, 'name_update_error'))


@dp.message_handler(state=Update.Phnum)
async def set_number(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_language = user_languages.get(user_id, 'default_language')
    async with state.proxy() as data:
        chat_id = message.chat.id
        new_number = message.text
        if re.match(r'^\+998\d{9}$', new_number):
            old_data = await state.get_data()
            db.update_user(chat_id, name=old_data.get('name'), phnum=new_number)
            await state.finish()
            await message.answer(get_text(user_language, 'num_update'), reply_markup=keyboard.get_back_keyboard(user_language))
        else:
            await message.answer(get_text(user_language, 'num_update_error'))


def get_calendar_menu(year, month, selected_day=None, selected_month=None, user_language='default_language'):
    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month
    current_day = current_date.day
    max_days = calendar.monthrange(year, month)[1]
    if user_language == "ru":
        month_names = [
            "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ]
    else:
        month_names = [
            "Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
            "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr"
        ]
    keyboard = InlineKeyboardMarkup(row_width=2)
    next_month = (month + 1) % 12
    row = []
    if year == current_year and month != current_month:
        row.append(InlineKeyboardButton("◀️", callback_data=f'prev:{year}-{month:02d}'))
    row.append(InlineKeyboardButton(
        text=month_names[month - 1],
        callback_data=f'month:{year}-{month:02d}'
    ))
    if (year == current_year and next_month >= current_month and next_month != current_month + 2) or (
            year > current_year):
        row.append(InlineKeyboardButton("▶️", callback_data=f'next:{year}-{next_month:02d}'))
    keyboard.row(*row)
    day_buttons = []
    day_row = []
    for day in range(1, max_days + 1):
        if (year == current_year and month == current_month and day < current_day) or (
                year == current_year and month < current_month):
            continue
        appointments_on_day = db.get_appointments_on_day(db.session, year, month, day)
        available_hours = db.get_available_hours(appointments_on_day)
        if available_hours:
            button_text = f"{day} ✅" if selected_day == day and selected_month == month else str(day)
            button = InlineKeyboardButton(text=button_text, callback_data=json.dumps(
                {'action': 'day', 'year': year, 'month': month, 'day': day}))
            day_row.append(button)
        else:
            button_text = f"{day} ❌" if selected_day == day and selected_month == month else f"{day} ❌"
            button = InlineKeyboardButton(text=button_text, callback_data=json.dumps(
                {'action': 'day', 'year': year, 'month': month, 'day': day}))
            day_row.append(button)
        if len(day_row) == 5:
            day_buttons.append(day_row)
            day_row = []
    if day_row:
        day_buttons.append(day_row)
    for row in day_buttons:
        keyboard.row(*row)
    keyboard.row(InlineKeyboardButton(get_text(user_language, 'choose_time'), callback_data='action:choose_time'))
    keyboard.row(InlineKeyboardButton(get_text(user_language, 'back'), callback_data='back'))
    return keyboard


def get_hour_menu(year, month, day, selected_hour=None, user_language='default_language'):
    start_hour = 8
    end_hour = 18
    keyboard = InlineKeyboardMarkup(row_width=3)
    appointments_on_day = db.get_appointments_on_day(db.session, year, month, day)
    available_hours = db.get_available_hours(appointments_on_day)

    for hour in range(start_hour, end_hour + 1):
        for minute in range(0, 60, 30):
            if hour == end_hour and minute > 0:
                break
            formatted_time = f"{hour:02d}:{minute:02d}"
            if formatted_time in available_hours:
                button_text = f"{formatted_time} ✅" if formatted_time == selected_hour else formatted_time
                button = InlineKeyboardButton(text=button_text, callback_data=f'hour:{formatted_time}')
                keyboard.insert(button)

    back_button = InlineKeyboardButton(get_text(user_language, 'back'), callback_data='back')
    keyboard.row(back_button)

    return keyboard


@dp.message_handler(text="📅 Запись на прием" or "📅 Uchrashuv belgilash", state='*')
async def start_appointment(message: types.Message):
    user_id = message.from_user.id
    user_language = user_languages.get(user_id, 'default_language')
    current_year = datetime.now().year
    current_month = datetime.now().month
    await message.answer(get_text(user_language, 'appointment1'), reply_markup=get_calendar_menu(current_year, current_month))
    await Appointments.SET_DAY.set()


@dp.callback_query_handler(lambda c: c.data.startswith('prev:') or c.data.startswith('next:'),
                           state=Appointments.SET_DAY)
async def navigate_calendar(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    user_language = user_languages.get(user_id, 'default_language')
    data = callback_query.data.split(':')
    direction = data[0]
    selected_year, selected_month = map(int, data[1].split('-'))
    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month

    if direction == 'prev':
        prev_month = (selected_month - 1) % 12
        prev_year = selected_year - 1 if prev_month == 0 else selected_year
        await callback_query.message.edit_text(get_text(user_language, 'appointment_day'), reply_markup=get_calendar_menu(prev_year, prev_month))
        await state.update_data(selected_month=prev_month)
    elif direction == 'next':
        next_month = (selected_month) % 12
        next_year = selected_year + 1 if next_month == 1 else selected_year
        await callback_query.message.edit_text(get_text(user_language, 'appointment_day'), reply_markup=get_calendar_menu(next_year, next_month))
        await state.update_data(selected_month=next_month)


@dp.callback_query_handler(lambda c: c.data.startswith('{"action": "day",'), state=[Appointments.SET_DAY, Appointments.SET_HOUR])
async def set_day(callback_query: CallbackQuery, state: FSMContext):
    print('я тут')
    print(callback_query.data)
    state_data = await state.get_data()
    print(state_data)
    if callback_query.data != 'back':
        await state.finish()
        data = json.loads(callback_query.data)
        selected_year = data.get('year')
        selected_month = data.get('month')
        selected_day = data.get('day')
        await state.update_data(selected_year=selected_year, selected_month=selected_month, selected_day=selected_day)
        reply_markup = get_calendar_menu(selected_year, selected_month, selected_day, selected_month)
    else:
        selected_year = state_data.get('selected_year')
        selected_month = state_data.get('selected_month')
        selected_day = state_data.get('selected_day')
        reply_markup = get_calendar_menu(selected_year, selected_month, selected_day, selected_month)
    await Appointments.SET_HOUR.set()
    await callback_query.message.edit_reply_markup(reply_markup=reply_markup)


@dp.callback_query_handler(lambda c: c.data == 'action:choose_time', state=Appointments.SET_HOUR)
async def choose_time(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    user_language = user_languages.get(user_id, 'default_language')
    print('я тут')
    data = await state.get_data()
    selected_year = data.get('selected_year')
    selected_month = data.get('selected_month')
    selected_day = data.get('selected_day')
    keyboard = get_hour_menu(selected_year, selected_month, selected_day)
    msg_info = get_text(user_language, 'appointment2')
    full_msg = msg_info.format(
        selected_day=data['selected_day'],
        selected_month = russian_month_names[data['selected_month'] - 1],
        selected_year=data['selected_year'],
    )
    await callback_query.message.edit_text(full_msg, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    await Appointments.SET_HOUR_CHOOSE.set()


@dp.callback_query_handler(lambda c: c.data.startswith('hour:'), state=Appointments.SET_HOUR_CHOOSE)
async def set_hour_choose(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    user_language = user_languages.get(user_id, 'default_language')
    print(callback_query.data)
    selected_hour = callback_query.data.split(':')[1]
    selected_minute = callback_query.data.split(':')[-1]
    print(f'hour {selected_hour}:{selected_minute}')
    data = await state.get_data()
    selected_month = data.get('selected_month')
    selected_day = data.get('selected_day')

    if selected_month is None:
        selected_month = datetime.now().month
    if selected_day is None:
        await callback_query.answer(get_text(user_language, 'day_error'))
        return
    try:
        appointment_time = datetime(
            year=datetime.now().year,
            month=selected_month,
            day=selected_day,
            hour=int(selected_hour),
            minute=int(selected_minute)
        )
    except TypeError:
        await callback_query.answer(get_text(user_language, 'time_error'))
        return

    await callback_query.message.edit_text(get_text(user_language, 'appointment3'), reply_markup=keyboard.get_back_keyboard(user_language), parse_mode=ParseMode.HTML)
    await state.update_data(appointment_time=appointment_time, selected_hour=selected_hour)
    await Appointments.SET_REASON.set()


@dp.message_handler(lambda message: True, state=Appointments.SET_REASON)
async def save_appointment_reason(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_language = user_languages.get(user_id, 'default_language')
    async with state.proxy() as data:
        appointment_time = data['appointment_time']
        chat_id = message.chat.id
        user_info = db.get_user_info(chat_id)
        user_id = message.from_user.id
        data['reason'] = message.text.strip()
        name = user_info['name']
        phnum = user_info['phnum']

        appointment_date = appointment_time.strftime(f"%d {keyboard.russian_month_names[appointment_time.month - 1]} %Y года")
        appointment_time_str = appointment_time.strftime("%H:%M")

        confirmation_message = get_text(user_language, 'confirmation-message')
        filled_confirmation_message = confirmation_message.format(
            name=name,
            phnum=phnum,
            appointment_date=appointment_date,
            appointment_time_str=appointment_time_str,
            reason=data['reason']
        )

        await message.answer(
            text=filled_confirmation_message,
            reply_markup=keyboard.get_app_confirm_keyboard(user_language)
        )


@dp.callback_query_handler(lambda c: c.data == 'confirm', state=Appointments.SET_REASON)
async def add_appointment_to_db(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    user_language = user_languages.get(user_id, 'default_language')
    async with state.proxy() as data:
        appointment_time = data['appointment_time']
        selected_hour = data['selected_hour']
        chat_id = callback_query.from_user.id
        user_info = db.get_user_info(chat_id)
        user_id = callback_query.from_user.id
        reason = data['reason']
        name = user_info['name']
        phnum = user_info['phnum']
        appointment_date = appointment_time.strftime(
            f"%d {keyboard.russian_month_names[appointment_time.month - 1]} %Y года")
        appointment_time_str = appointment_time.strftime("%H:%M")
        db.create_appointment(user_id, callback_query.from_user.username, name, phnum, reason, appointment_time)
        current_state = await state.get_state()
        confirmation_message = get_text(user_language, 'confirmation-message2')
        filled_confirmation_message = confirmation_message.format(
            name=name,
            phnum=phnum,
            appointment_date=appointment_date,
            appointment_time_str=appointment_time_str,
            reason=data['reason']
        )

        if current_state == 'Appointment.SET_REASON':
            await callback_query.message.edit_text(filled_confirmation_message,
                                                   reply_markup=keyboard.get_back_keyboard(user_language), parse_mode="HTML")
        else:
            await callback_query.message.edit_text(filled_confirmation_message, parse_mode="HTML")
        await state.finish()

        group_chat_id = -921482477

        confirmation_group = (
            f"🆕 Новая запись в стоматологию\n"
            f"<b>ФИО</b>: {name}\n"
            f"<b>Номер телефона</b>: {phnum}\n"
            f"<b>Дата записи</b>: {appointment_date}\n"
            f"<b>Время записи</b>: {appointment_time_str}\n"
            f"<b>Описание симптомов/цель визита</b>: {data['reason']}\n\n\n"
            f"<i>Пожалуйста, учтите данную запись в расписании и подготовьте все необходимое для приема.</i>"
        )

        await bot.send_message(chat_id=group_chat_id, text=confirmation_group, parse_mode="HTML")
        time_until_notification_24h = appointment_time - timedelta(hours=24)
        time_until_notification_1h = appointment_time - timedelta(hours=1)

        asyncio.create_task(send_notification_24h(chat_id, time_until_notification_24h, reason, data, user_language))
        asyncio.create_task(send_notification_1h(chat_id, time_until_notification_1h, reason, data, user_language))


import asyncio


async def send_notification_24h(chat_id, notification_time, reason, data, user_language):
    await asyncio.sleep((notification_time - datetime.now()).total_seconds())
    appointment_time = data['appointment_time']
    appointment_date = appointment_time.strftime(f"%d {keyboard.russian_month_names[appointment_time.month - 1]} %Y года")
    appointment_time_str = appointment_time.strftime("%H:%M")

    notification_text24 = get_text(user_language, 'notification-message24')
    filled_confirmation_message24 = notification_text24.format(
        appointment_date=appointment_date,
        appointment_time_str=appointment_time_str,
        reason=data['reason']
    )

    await bot.send_message(chat_id, filled_confirmation_message24)


async def send_notification_1h(chat_id, notification_time, reason, data, user_id):
    await asyncio.sleep((notification_time - datetime.now()).total_seconds())
    appointment_time = data['appointment_time']
    appointment_time_str = appointment_time.strftime("%H:%M")
    notification_text1 = (get_text(user_language, 'notification-message1'))
    filled_confirmation_message1 = notification_text1.format(
        appointment_time_str=appointment_time_str,
        reason=data['reason']
    )

    await bot.send_message(chat_id, filled_confirmation_message1)



user_view_modes = {}


@dp.callback_query_handler(lambda c: c.data == 'my_app', state="*")
async def show_appointments(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    user_language = user_languages.get(user_id, 'default_language')
    chat_id = callback_query.from_user.id

    if chat_id not in user_view_modes:
        user_view_modes[chat_id] = "booked"

    current_view_mode = user_view_modes[chat_id]
    appointments = db.get_appointments(db.session, chat_id, current_view_mode)
    if appointments:
        message_text = get_text(user_language, 'my_app')
        keyboard = InlineKeyboardMarkup()

        for idx, appointment in enumerate(appointments, start=1):
            appointment_date = appointment.time.strftime(
                f"%d {russian_month_names[appointment.time.month - 1]} %Y года").lstrip('0')
            appointment_time_str = appointment.time.strftime("%H:%M")
            appointment_reason = appointment.reason
            button_text = f"{appointment_date}, {appointment_time_str}"
            button = InlineKeyboardButton(text=button_text, callback_data=f'app_info:{idx}')
            keyboard.add(button)
            message_text += f"<b>{idx}</b>. {appointment_date}, {appointment_time_str} - {appointment_reason}\n"
        if current_view_mode == "booked":
            toggle_mode_button_text = get_text(user_language, 'show_canceled')
            next_view_mode = "canceled"
        else:
            toggle_mode_button_text = get_text(user_language, 'show_current')
            next_view_mode = "booked"

        toggle_mode_button = InlineKeyboardButton(
            text=toggle_mode_button_text,
            callback_data=f'toggle_view_mode:{next_view_mode}'
        )
        keyboard.add(toggle_mode_button)
        back_button = InlineKeyboardButton(get_text(user_language, 'back'), callback_data='back')
        keyboard.add(back_button)
        message_text += '\n\n\n'
        message_text += get_text(user_language, 'app_choose')
        await callback_query.message.edit_text(message_text, reply_markup=keyboard)
    else:
        # Добавляем кнопки для переключения режимов
        if current_view_mode == "booked":
            toggle_mode_button_text = get_text(user_language, 'show_canceled')
            next_view_mode = "canceled"
        else:
            toggle_mode_button_text = get_text(user_language, 'show_current')
            next_view_mode = "booked"

        toggle_mode_button = InlineKeyboardButton(
            text=toggle_mode_button_text,
            callback_data=f'toggle_view_mode:{next_view_mode}'
        )
        keyboard = InlineKeyboardMarkup()
        keyboard.add(toggle_mode_button)
        back_button = InlineKeyboardButton(get_text(user_language, 'back'), callback_data='back')
        keyboard.add(back_button)
        await callback_query.message.edit_text(get_text(user_language, 'no_app'), reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data.startswith('toggle_view_mode:'))
async def toggle_view_mode(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    user_language = user_languages.get(user_id, 'default_language')
    chat_id = callback_query.from_user.id

    if chat_id in user_view_modes:
        current_view_mode = user_view_modes[chat_id]
        next_view_mode = callback_query.data.split(':')[1]
        user_view_modes[chat_id] = next_view_mode
        await show_appointments(callback_query, None)


@dp.callback_query_handler(lambda c: c.data.startswith('app_info:'), state="*")
async def show_appointment_info(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    user_language = user_languages.get(user_id, 'default_language')
    app_index = int(callback_query.data.split(':')[1])
    chat_id = callback_query.from_user.id
    current_view_mode = user_view_modes[chat_id]
    appointments = db.get_appointments(db.session, chat_id, current_view_mode)

    if 1 <= app_index <= len(appointments):
        selected_appointment = appointments[app_index - 1]
        appointment_date = selected_appointment.time.strftime(
            f"%e {russian_month_names[selected_appointment.time.month - 1]} %Y года")
        appointment_time_str = selected_appointment.time.strftime("%H:%M")
        appointment_reason = selected_appointment.reason  # Получаем причину записи
        appointment_info_template = get_text(user_language, 'appointment_info')
        filled_confirmation_message = appointment_info_template.format(
            appointment_date=appointment_date,
            appointment_time_str=appointment_time_str,
            appointment_reason=appointment_reason
        )

        if current_view_mode == "booked":
            full_appointment_info = appointment_info_template.format(
                appointment_date=appointment_date,
                appointment_time_str=appointment_time_str,
                appointment_reason=appointment_reason
            ) + '\n\n\n' + get_text(user_language, 'appointment_info1')
            await callback_query.message.edit_text(full_appointment_info,
                                                   reply_markup=keyboard.get_cancel_keyboard(user_language), parse_mode='HTML')

            await state.update_data(
                appointment_id=selected_appointment.id,
                selected_day=selected_appointment.time.day,
                selected_month=selected_appointment.time.month,
                selected_year=selected_appointment.time.year,
                selected_hour=selected_appointment.time.hour,
                selected_minute=selected_appointment.time.minute,
                appointment_reason=appointment_reason
            )
            await Appointments.CANCEL_CONFIRM.set()
        else:
            await callback_query.message.edit_text(filled_confirmation_message,
                                                   reply_markup=keyboard.get_back_keyboard(user_language), parse_mode='HTML')
    else:
        await callback_query.answer(get_text(user_language, 'wrong_app'))


@dp.callback_query_handler(lambda c: c.data == 'cancel', state=Appointments.CANCEL_CONFIRM)
async def cancel_appointment_confirm(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    user_language = user_languages.get(user_id, 'default_language')
    data = await state.get_data()
    appointment_id = data.get('appointment_id')

    if appointment_id:
        cancel_confirmation_message = get_text(user_language, 'cancel-confirmation')
        filled_cancel_confirmation_message = cancel_confirmation_message.format(
            selected_day=data['selected_day'],
            selected_month=russian_month_names[data['selected_month'] - 1],
            selected_year=data['selected_year'],
            selected_hour=data['selected_hour'],
            selected_minute=data['selected_minute']
        )
        await callback_query.message.edit_text(filled_cancel_confirmation_message, reply_markup=keyboard.get_del_confirm_keyboard(user_language))
        await Appointments.DELETE_CONFIRM.set()
    else:
        await callback_query.message.edit_text(get_text(user_language, 'cannot-delete-cancelled-appointment'))


@dp.callback_query_handler(lambda c: c.data == 'del_confirm', state=Appointments.DELETE_CONFIRM)
async def delete_appointment_confirm(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    user_language = user_languages.get(user_id, 'default_language')
    data = await state.get_data()
    appointment_id = data.get('appointment_id')
    if appointment_id:
        await callback_query.message.edit_text(get_text(user_language, 'cancellation-reason-prompt'),
                                               reply_markup=keyboard.get_back_keyboard(user_language))
        await Appointments.DELETE_REASON.set()
    else:
        await callback_query.answer(get_text(user_language, 'error-occurred'))


@dp.message_handler(state=Appointments.DELETE_REASON)
async def set_cancel_reason(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_language = user_languages.get(user_id, 'default_language')
    cancel_reason = message.text
    await state.update_data(cancel_reason=cancel_reason)
    data = await state.get_data()
    appointment_id = data.get('appointment_id')
    if appointment_id:
        deleted = db.delete_appointment(db.session, appointment_id)
        if deleted:
            appointment_date = data['selected_day']
            appointment_month = russian_month_names[data['selected_month'] - 1]
            appointment_year = data['selected_year']
            appointment_time = f"{data['selected_hour']}:{data['selected_minute']}"
            appointment_reason = data.get('appointment_reason', '')

            chat_id = message.chat.id
            user_info = db.get_user_info(chat_id)
            name = user_info['name']
            phnum = user_info['phnum']

            cancel_reason = data['cancel_reason']
            group_chat_id = -921482477
            cancel_group = (
                f"🚫 Запись в стоматологию отменена\n"
                f"<b>ФИО</b>: {name}\n"
                f"<b>Номер телефона</b>: {phnum}\n"
                f"<b>Дата записи</b>: {appointment_date} {appointment_month} {appointment_year} года\n"
                f"<b>Время записи</b>: {appointment_time}\n"
                f"<b>Симптомы/цель визита</b>: {appointment_reason}\n"
                f"<b>Причина отмены</b>: {cancel_reason}\n\n\n"
                f"<i>Пожалуйста, учтите данную отмену в расписании.</i>"
            )
            await bot.send_message(group_chat_id, cancel_group, parse_mode='HTML')
            cancel_info = get_text(user_language, 'appointment-cancelled-successfully')
            filled_cancel_confirmation = cancel_info.format(
                appointment_date=appointment_date,
                appointment_month=appointment_month,
                appointment_year=appointment_year,
                appointment_time=appointment_time,
            )
            await message.answer(filled_cancel_confirmation, reply_markup=keyboard.get_back_keyboard(user_language)
            )
        else:
            await message.answer(get_text(user_language, 'error-occurred-cancelling-appointment'))
    else:
        await message.answer(get_text(user_language, 'error-occurred'))

    await state.finish()


def delete_expired_appointments():
    current_time = datetime.now()
    session = Session()
    expired_appointments = session.query(Appointment).filter(current_time > Appointment.time).all()
    for appointment in expired_appointments:
        session.delete(appointment)
    session.commit()
    session.close()


scheduler = AsyncIOScheduler()

scheduler.add_job(delete_expired_appointments, trigger=CronTrigger(minute='*'))

scheduler.start()


async def run_bot():
    while True:
        await asyncio.sleep(1)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())
    from aiogram import executor
    from admin import *
    executor.start_polling(dp, skip_updates=True)