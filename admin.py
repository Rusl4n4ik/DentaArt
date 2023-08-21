import asyncio
import calendar
import json
import math
import re
from datetime import datetime, timedelta

from aiogram import types
from charset_normalizer import md

from main import navigate_calendar
from aiogram.dispatcher.filters import Text, state
from aiogram.types import ReplyKeyboardRemove, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from aiogram.utils.callback_data import CallbackData
from fsm import Admins, Appointment, Offline
from main import dp, bot
import db, keyboard, main
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from fsm import Users, Update


@dp.message_handler(commands=['admin'])
async def admin_panel(message: types.Message):
    chat_id = message.chat.id
    if db.is_admin(chat_id):
        db.add_admin(chat_id, message.from_user.first_name, message.from_user.username)
        await message.answer("🛠 Выберите действие:", reply_markup=keyboard.admin_keyboard)
    else:
        await message.answer("У вас нет доступа к админ-панели.")


@dp.callback_query_handler(lambda c: c.data == 'back_ad', state='*')
async def go_back(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    state_data = await state.get_data()
    print(current_state)
    if current_state == 'Admins:HOUR_CHOOSE':
        await state.reset_state()
        await show_admin_calendar_from_button(callback)
    elif current_state == 'Offline:SET_HOUR':
        await state.reset_state()
        await set_phnum_offline(callback, state)
    elif current_state == 'Offline:SET_REASON':
        await choose_time(callback, state)
    else:
        await callback.message.answer("🛠 Выберите действие:", reply_markup=keyboard.admin_keyboard)


@dp.callback_query_handler(text="broadcast", state="*")
async def broadcast_button_handler(callback_query: CallbackQuery, state: FSMContext):
    chat_id = callback_query.from_user.id
    if db.is_admin(chat_id):
        await callback_query.answer()
        await callback_query.message.edit_text("Выберите опцию рассылки:", reply_markup=keyboard.broadcast_option_menu)
        await Admins.Broadcast.set()
    else:
        await callback_query.answer("Вы не являетесь администратором.")


@dp.callback_query_handler(text="broadcast_option", state=Admins.Broadcast)
async def broadcast_option_handler(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.edit_text("Выберите опцию рассылки:", reply_markup=keyboard.broadcast_option_menu)


@dp.callback_query_handler(text="broadcast_all", state=Admins.Broadcast)
async def broadcast_all_handler(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.answer("Введите текст сообщения для рассылки:", reply_markup=keyboard.back_admin)
    await Admins.BroadcastTextAll.set()


@dp.callback_query_handler(text="broadcast_with_appointments", state=Admins.Broadcast)
async def broadcast_with_appointments_handler(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.answer("Введите текст сообщения для рассылки пользователям с записями:", reply_markup=keyboard.back_admin)
    await Admins.BroadcastTextAppointments.set()


@dp.message_handler(commands=("cancel"), state=Admins.Broadcast)
@dp.message_handler(Text(equals="/cancel", ignore_case=True), state=Admins.Broadcast)
async def cancel_broadcast(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Рассылка отменена.", reply_markup=keyboard.back_admin)


@dp.message_handler(state=Admins.BroadcastTextAll)
async def process_broadcast_all(message: types.Message, state: FSMContext):
    users = db.get_all_users()
    total_users = len(users)
    if total_users >= 1:
        for user in users:
            chat_id = user['chat_id']
            await bot.send_message(chat_id, message.text)
        await state.finish()
        await message.answer(f"Сообщение успешно отправлено {total_users} пользователям.", reply_markup=keyboard.back_admin)
    else:
        await state.finish()
        await message.answer("Нет доступных пользователей для рассылки.", reply_markup=keyboard.back_admin)


@dp.message_handler(state=Admins.BroadcastTextAppointments)
async def process_broadcast_appointments(message: types.Message, state: FSMContext):
    users_with_appointments = db.get_users_with_appointments(db.session)
    total_users = len(users_with_appointments)
    if total_users >= 1:
        for user in users_with_appointments:
            chat_id = user.chat_id
            await bot.send_message(chat_id, message.text)
        await state.finish()
        await message.answer(f"Сообщение успешно отправлено {total_users} пользователям с записями.", reply_markup=keyboard.back_admin)
    else:
        await state.finish()
        await message.answer("Нет пользователей с записями для рассылки.", reply_markup=keyboard.back_admin)


@dp.callback_query_handler(lambda c: c.data == 'admin_show_users')
async def admin_show_users(callback: types.CallbackQuery):
    users = db.get_all_users()
    if users:
        page = 0
        per_page = 1  # Количество пользователей на странице
        total_pages = (len(users) + per_page - 1) // per_page

        user_list = ""
        for idx, user in enumerate(users[page * per_page:(page + 1) * per_page], start=page * per_page + 1):
            appointments = db.get_appointments(db.session, user['chat_id'])
            appointments_info = ', '.join([appointment.time.strftime('%d %b %Y %H:%M') for appointment in appointments])
            user_info = f"<b>{idx}</b>. {user['name']}:\n{user['phnum']}\n"
            if appointments_info:
                user_info += "<b>📝 Предстоящие записи:</b>\n"
                for appointment in appointments:
                    appointment_date = appointment.time.strftime(
                        f"%e {keyboard.russian_month_names[appointment.time.month - 1]} %Y года")
                    appointment_time_str = appointment.time.strftime("%H:%M")
                    user_info += f"{appointment_date} в {appointment_time_str}\n"
            user_list += user_info + "\n"

        navigation_buttons = []
        if page > 0:
            navigation_buttons.append(
                InlineKeyboardButton("⬅️", callback_data=f"admin_show_users_page:{page - 1}"))
        if page < total_pages - 1:
            navigation_buttons.append(
                InlineKeyboardButton("➡️", callback_data=f"admin_show_users_page:{page + 1}"))

        reply_markup = InlineKeyboardMarkup().add(*navigation_buttons)

        await callback.answer()
        await callback.message.edit_text(f"Список пользователей:\n{user_list}", reply_markup=reply_markup, parse_mode="HTML")
    else:
        await callback.answer("Нет зарегистрированных пользователей.")


@dp.callback_query_handler(lambda c: c.data.startswith('admin_show_users_page:'))
async def admin_show_users_page(callback: types.CallbackQuery):
    page = int(callback.data.split(':')[1])
    users = db.get_all_users()
    per_page = 1  # Количество пользователей на странице
    total_pages = (len(users) + per_page - 1) // per_page

    user_list = ""
    for idx, user in enumerate(users[page * per_page:(page + 1) * per_page], start=page * per_page + 1):
        appointments = db.get_appointments(db.session, user['chat_id'])
        appointments_info = ', '.join([appointment.time.strftime('%d %b %Y %H:%M') for appointment in appointments])
        user_info = f"<b>{idx}</b>. {user['name']}:\n{user['phnum']}\n"
        if appointments_info:
            user_info += "<b>📝 Предстоящие записи:</b>\n"
            for appointment in appointments:
                appointment_date = appointment.time.strftime(
                    f"%e {keyboard.russian_month_names[appointment.time.month - 1]} %Y года")
                appointment_time_str = appointment.time.strftime("%H:%M")
                user_info += f"{appointment_date} в {appointment_time_str}\n"
        if len(user_list + user_info) >= 4096:
            break
        user_list += user_info + "\n"

    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(
            InlineKeyboardButton("⬅️", callback_data=f"admin_show_users_page:{page - 1}"))
    if page < total_pages - 1:
        navigation_buttons.append(
            InlineKeyboardButton("➡️", callback_data=f"admin_show_users_page:{page + 1}"),)
    reply_markup = InlineKeyboardMarkup(row_width=2)
    for button in navigation_buttons:
        reply_markup.insert(button)
    reply_markup.row(keyboard.back_ad)

    await callback.message.edit_text(f"Список пользователей:\n{user_list}", reply_markup=reply_markup, parse_mode="HTML")


def get_user_appointments_info(user):
    appointments = db.get_user_appointments(db.session, user['chat_id'])
    if appointments:
        appointments_info = ', '.join([appointment.time.strftime('%d %b %Y %H:%M') for appointment in appointments])

        return appointments_info
    return None


@dp.message_handler(commands=['add_service'])
async def add_service_command(message: types.Message):
    if db.is_admin(message.chat.id):
        await message.answer("Введите название новой услуги:")
        await Admins.AddServiceName.set()
    else:
        await message.answer("Вы не являетесь администратором.")


@dp.message_handler(state=Admins.AddServiceName)
async def add_service_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await Admins.AddServicePrice.set()
    await message.answer("Введите цену для новой услуги:")


@dp.message_handler(lambda message: True, state=Admins.AddServicePrice)
async def add_service_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        name = data['name']
    price = message.text
    db.add_price_and_service(name, price)
    await message.answer(f"Услуга '{name}' с ценой {price} успешно добавлена в прайс-лист.")
    await state.finish()


@dp.callback_query_handler(text="price_list")
async def show_price_list(callback_query: CallbackQuery):
    await callback_query.answer()

    prices = db.get_all_prices()
    price_list_text = '💵 Прайс-лист стоматологии "Denta Art":\n'
    for index, price in enumerate(prices, start=1):
        price_list_text += f"{index}. <b>{price.service}:</b> {price.price}\n"
    await callback_query.message.answer(price_list_text, reply_markup=keyboard.price_list)


@dp.callback_query_handler(text="ch_price")
async def edit_price_list(callback_query: CallbackQuery):
    await callback_query.answer()

    prices = db.get_all_prices()
    markup = keyboard.create_price_edit_keyboard(prices)

    await callback_query.message.answer("Выберите услугу, для которой вы хотите изменить название или прайс:",
                                        reply_markup=markup)


@dp.callback_query_handler(keyboard.price_edit_callback.filter())
async def edit_selected_service(callback_query: CallbackQuery, callback_data: dict):
    await callback_query.answer()

    service_index = int(callback_data["service_index"])
    selected_service = db.get_price_by_index(service_index)  # Исправлено здесь

    if selected_service:
        buttons = [
            InlineKeyboardButton('Изменить название', callback_data=f"edit_name:{service_index}"),
            InlineKeyboardButton('Изменить прайс', callback_data=f"ed_price:{service_index}"),
            InlineKeyboardButton('🔙 Назад', callback_data='ch_price')
        ]

        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(*buttons)

        await callback_query.message.answer(f"Выберите действие для услуги '{selected_service.service}':",
                                            reply_markup=markup)
    else:
        await callback_query.message.answer("Услуга не найдена.", reply_markup=keyboard.price_list)


@dp.callback_query_handler(lambda c: c.data.startswith("ed_price:"), state="*")
async def edit_service_price(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    service_index = int(callback_query.data.split(":")[1])
    await callback_query.message.answer(f"Введите новый прайс для услуги '{service_index + 1}':")

    async with state.proxy() as data:
        data["editing_service"] = service_index

    await Admins.EditPriceAmount.set()


@dp.message_handler(lambda message: True, state=Admins.EditPriceAmount)
async def save_new_service_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        service_index = data["editing_service"]

    new_price = message.text.strip()

    if new_price:
        service = db.get_price_by_index(service_index)
        if service:
            session = db.Session()
            db.update_service_price(session, service.service, new_price)
            session.close()
            await message.answer("Новый прайс успешно сохранен.", reply_markup=keyboard.back_admin)
        else:
            await message.answer("Услуга не найдена.")
    else:
        await message.answer("Изменения не сохранены.")

    await state.finish()


@dp.callback_query_handler(text='view_app')
async def view_appointments(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    appointments = db.get_all_appointments(db.session)  # Получите список всех записей

    page_size = 5  # Количество записей на одной странице
    page_number = 1  # Номер текущей страницы

    start_idx = (page_number - 1) * page_size
    end_idx = min(start_idx + page_size, len(appointments))

    if appointments:
        message = f"Список записей (страница {page_number}/{math.ceil(len(appointments) / page_size)}):\n\n"
        for idx, appointment in enumerate(appointments[start_idx:end_idx], start=start_idx + 1):
            appointment_date = appointment.time.strftime(
                f"%d {keyboard.russian_month_names[appointment.time.month - 1]} %Y года").lstrip('0')
            appointment_time_str = appointment.time.strftime("%H:%M")
            appointment_reason = appointment.reason

            user_info = db.get_user_info(appointment.chat_id)
            if user_info:
                user_name = user_info['name']
                user_phnum = user_info['phnum']
            else:
                user_name = "Информация недоступна"
                user_phnum = "Информация недоступна"

            message += (
                f"<b>Запись #{idx}</b>\n"
                f"<b>Дата записи:</b> {appointment_date}\n"
                f"<b>Время записи:</b> {appointment_time_str}\n"
                f"<b>Пациент:</b> {user_name}\n"
                f"<b>Номер телефона:</b> {user_phnum}\n"
                f"<b>Симптомы/цель визита:</b> {appointment_reason}\n\n"
            )

        # Добавление кнопок для перехода по страницам
        navigation_buttons = []
        if len(appointments) > end_idx:
            navigation_buttons.append(
                InlineKeyboardButton("➡️ Следующая страница", callback_data="view_app_next_page"))
        if page_number > 1:
            navigation_buttons.append(
                InlineKeyboardButton("⬅️ Предыдущая страница", callback_data="view_app_prev_page"))

        if navigation_buttons:
            reply_markup = InlineKeyboardMarkup(row_width=1)
            for button in navigation_buttons:
                reply_markup.insert(button)
            reply_markup.row(keyboard.back_ad)
        else:
            reply_markup = InlineKeyboardMarkup().add(keyboard.back_ad)

        await callback_query.message.edit_text(message, reply_markup=reply_markup, parse_mode='HTML')


@dp.callback_query_handler(text='view_app_next_page')
async def view_app_next_page(callback_query: CallbackQuery):
    await view_app_page_navigation(callback_query, forward=True)


@dp.callback_query_handler(text='view_app_prev_page')
async def view_app_prev_page(callback_query: CallbackQuery):
    await view_app_page_navigation(callback_query, forward=False)


async def view_app_page_navigation(callback_query: CallbackQuery, forward: bool):
    await callback_query.answer()

    page_number = int(callback_query.data.split(':')[1]) if ':' in callback_query.data else 1

    if forward:
        page_number += 1
    else:
        page_number -= 1

    await view_app_page_update(callback_query, page_number)


@dp.callback_query_handler(lambda c: c.data.startswith('view_app_page:'))
async def view_app_page(callback_query: CallbackQuery):
    await callback_query.answer()

    page_number = int(callback_query.data.split(':')[1])  # Получите номер страницы из callback_query

    await view_app_page_update(callback_query, page_number)


async def view_app_page_update(callback_query: CallbackQuery, page_number: int):
    appointments = db.get_all_appointments(db.session)  # Получите список всех записей

    page_size = 5  # Количество записей на одной странице

    start_idx = (page_number - 1) * page_size
    end_idx = min(start_idx + page_size, len(appointments))

    if appointments:
        message = f"Список записей (страница {page_number}/{math.ceil(len(appointments) / page_size)}):\n\n"
        for idx, appointment in enumerate(appointments[start_idx:end_idx], start=start_idx + 1):
            appointment_date = appointment.time.strftime(
                f"%d {keyboard.russian_month_names[appointment.time.month - 1]} %Y года").lstrip('0')
            appointment_time_str = appointment.time.strftime("%H:%M")
            appointment_reason = appointment.reason

            user_info = db.get_user_info(appointment.chat_id)
            if user_info:
                user_name = user_info['name']
                user_phnum = user_info['phnum']
            else:
                user_name = "Информация недоступна"
                user_phnum = "Информация недоступна"

            message += (
                f"<b>Запись #{idx}</b>\n"
                f"<b>Дата записи:</b> {appointment_date}\n"
                f"<b>Время записи:</b> {appointment_time_str}\n"
                f"<b>Пациент:</b> {user_name}\n"
                f"<b>Номер телефона:</b> {user_phnum}\n"
                f"<b>Симптомы/цель визита:</b> {appointment_reason}\n\n"
            )

        # Добавление кнопок для перехода по страницам
        navigation_buttons = []

        if page_number > 1:
            navigation_buttons.append(
                InlineKeyboardButton("⬅️ Предыдущая страница", callback_data=f"view_app_page:{page_number - 1}"))

        if end_idx < len(appointments):
            navigation_buttons.append(
                InlineKeyboardButton("➡️ Следующая страница", callback_data=f"view_app_page:{page_number + 1}"))

        reply_markup = InlineKeyboardMarkup(row_width=1)
        for button in navigation_buttons:
            reply_markup.insert(button)
        reply_markup.row(keyboard.back_ad)

        await callback_query.message.edit_text(message, reply_markup=reply_markup, parse_mode='HTML')


def get_calendar_menu(year, month, selected_day=None, selected_month=None):
    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month
    current_day = current_date.day

    max_days = calendar.monthrange(year, month)[1]

    # Собственные названия месяцев на русском языке
    month_names = [
        "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
        "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
    ]

    keyboard = InlineKeyboardMarkup(row_width=2)

    next_month = (month + 1) % 12
    row = []
    if year == current_year and month != current_month:
        row.append(InlineKeyboardButton("◀️", callback_data=f'prev:{year}-{month:02d}'))
    row.append(InlineKeyboardButton(
        text=month_names[month - 1],  # Индексы начинаются с 0
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

    keyboard.row(InlineKeyboardButton("🕘 Выбрать время", callback_data='action:choose_time'))
    keyboard.row(InlineKeyboardButton("🔙Назад", callback_data='back_ad'))

    return keyboard


def get_hour_menu(year, month, day, selected_hour=None):
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

    back_button = InlineKeyboardButton("🔙Назад", callback_data='back_ad')
    keyboard.row(back_button)

    return keyboard


@dp.callback_query_handler(lambda c: c.data.startswith('prev:') or c.data.startswith('next:'),)
async def navigate_calendar(callback_query: CallbackQuery, state: FSMContext):
    data = callback_query.data.split(':')
    direction = data[0]  # 'prev' or 'next'
    selected_year, selected_month = map(int, data[1].split('-'))
    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month

    if direction == 'prev':
        prev_month = (selected_month - 1) % 12
        prev_year = selected_year - 1 if prev_month == 0 else selected_year
        await callback_query.message.edit_text("Выберите день:", reply_markup=get_calendar_menu(prev_year, prev_month))
        await state.update_data(selected_month=prev_month)
    elif direction == 'next':
        next_month = (selected_month) % 12
        next_year = selected_year + 1 if next_month == 1 else selected_year
        await callback_query.message.edit_text("Выберите день:", reply_markup=get_calendar_menu(next_year, next_month))
        await state.update_data(selected_month=next_month)


@dp.callback_query_handler(lambda c: c.data == 'calendar', state='*')
async def show_admin_calendar_from_button(callback_query: CallbackQuery):
    current_date = datetime.now()
    year = current_date.year
    month = current_date.month
    current_day = current_date.day
    await callback_query.message.edit_text("Выберите дату:", reply_markup=get_calendar_menu(year, month))
    await Admins.ViewDay.set()


@dp.callback_query_handler(lambda c: json.loads(c.data).get('action') == 'day', state=Admins.ViewDay)
async def set_day(callback_query: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    print(state_data)
    if not state_data.get('selected_year'):
        data = json.loads(callback_query.data)
        selected_year = data.get('year')
        selected_month = data.get('month')
        selected_day = data.get('day')

        await state.update_data(selected_year=selected_year, selected_month=selected_month, selected_day=selected_day)
        reply_markup = get_calendar_menu(selected_year, selected_month, selected_day=selected_day, selected_month=selected_month)

    else:
        selected_year = state_data.get('selected_year')
        selected_month = state_data.get('selected_month')
        selected_day = state_data.get('selected_day')
        reply_markup = get_calendar_menu(selected_year, selected_month, selected_day, selected_month)
    await Admins.ViewHour.set()
    await callback_query.message.edit_reply_markup(reply_markup=reply_markup)


@dp.callback_query_handler(lambda c: c.data == 'action:choose_time', state=Admins.ViewHour)
async def choose_time(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_year = data.get('selected_year')
    selected_month = data.get('selected_month')
    selected_day = data.get('selected_day')
    keyboard = get_hour_menu(selected_year, selected_month, selected_day)
    await callback_query.message.edit_text(text='Доступные временые слоты' ,reply_markup=keyboard)
    await Admins.HOUR_CHOOSE.set()


@dp.callback_query_handler(lambda c: c.data == 'offline_appointment')
async def offline_appointment(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer("📝 Введите ФИО в формате 'Фамилия Имя Отчество'", reply_markup=types.ReplyKeyboardRemove())
    await Offline.Name.set()


@dp.message_handler(state=Offline.Name)
async def set_name_offline(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        chat_id = message.chat.id
        new_name = message.text
        if re.match(r'^[А-ЯЁа-яё]+\s[А-ЯЁа-яё]+\s[А-ЯЁа-яё]+$', new_name):
            data['new_name'] = new_name
            await message.answer("Отлично! Теперь номер телефона в формате '+998XXXXXXXXX'.", reply_markup=types.ReplyKeyboardRemove())
            await Offline.Phnum.set()
        else:
            await message.answer("⚠️ Кажется, вы ввели ФИО в неправильном формате. Пожалуйста, убедитесь, что вы ввели ваше полное имя в формате 'Фамилия Имя Отчество'. Попробуйте еще раз:")


@dp.message_handler(state=Offline.Phnum)
async def set_phnum_offline(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        chat_id = message.chat.id
        new_phnum = message.text
        if re.match(r'^\+\d{12}$', new_phnum):
            data['new_phnum'] = new_phnum

            # Get the current year and month
            current_date = datetime.now()
            current_year = current_date.year
            current_month = current_date.month

            await message.answer(
                '📅 Чтобы записаться на приëм, выберите удобную для вас дату. Обратите внимание, что прошедшие даты недоступны для выбора.\n'
                'Воспользуйтесь календарём и для начала выберите дату. <b>После того как отметили дату галочкой, нажмите кнопку</b> "🕘 Выбрать время:"',
                reply_markup=get_calendar_offline(current_year, current_month))
            await Appointment.SET_DAY.set()
            old_data = await state.get_data()
            db.update_user(chat_id, name=data['new_name'], phnum=data['new_phnum'])

        else:
            await message.answer(
                "⚠️ Кажется, вы ввели номер телефона в неправильном формате. Пожалуйста, убедитесь, что вы ввели ваш номер в формате '+998XXXXXXXXX'. Попробуйте еще раз:")


def get_calendar_offline(year, month, selected_day=None, selected_month=None):
    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month
    current_day = current_date.day

    max_days = calendar.monthrange(year, month)[1]

    # Собственные названия месяцев на русском языке
    month_names = [
        "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
        "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
    ]

    keyboard = InlineKeyboardMarkup(row_width=2)

    next_month = (month + 1) % 12
    row = []
    if year == current_year and month != current_month:
        row.append(InlineKeyboardButton("◀️", callback_data=f'prev:{year}-{month:02d}'))
    row.append(InlineKeyboardButton(
        text=month_names[month - 1],  # Индексы начинаются с 0
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

    keyboard.row(InlineKeyboardButton("🕘 Выбрать время", callback_data='action:choose_time'))
    keyboard.row(InlineKeyboardButton("🔙Назад", callback_data='back_ad'))

    return keyboard


def get_hour_offline(year, month, day, selected_hour=None):
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

    back_button = InlineKeyboardButton("🔙Назад", callback_data='back_ad')
    keyboard.row(back_button)

    return keyboard


@dp.callback_query_handler(lambda c: c.data.startswith('prev:') or c.data.startswith('next:'),
                           state=Offline.SET_DAY)
async def navigate_calendar(callback_query: CallbackQuery, state: FSMContext):
    data = callback_query.data.split(':')
    direction = data[0]  # 'prev' or 'next'
    selected_year, selected_month = map(int, data[1].split('-'))
    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month

    if direction == 'prev':
        prev_month = (selected_month - 1) % 12
        prev_year = selected_year - 1 if prev_month == 0 else selected_year
        await callback_query.message.edit_text("Выберите день:", reply_markup=get_calendar_offline(prev_year, prev_month))
        await state.update_data(selected_month=prev_month)
    elif direction == 'next':
        next_month = (selected_month) % 12
        next_year = selected_year + 1 if next_month == 1 else selected_year
        await callback_query.message.edit_text("Выберите день:", reply_markup=get_calendar_offline(next_year, next_month))
        await state.update_data(selected_month=next_month)


@dp.callback_query_handler(lambda c: json.loads(c.data).get('action') == 'day', state=Offline.SET_DAY)
async def set_day_offline(callback_query: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    print(state_data)
    if not state_data.get('selected_year'):
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
    await Offline.SET_HOUR.set()

    # В этом месте также добавьте кнопку "Выбрать время"
    await callback_query.message.edit_reply_markup(reply_markup=reply_markup)


@dp.callback_query_handler(lambda c: c.data == 'action:choose_time', state=Offline.SET_HOUR)
async def choose_time_offline(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_year = data.get('selected_year')
    selected_month = data.get('selected_month')
    selected_day = data.get('selected_day')

    # Используйте обновленный get_hour_menu с галочкой
    keyboard = get_hour_offline(selected_year, selected_month, selected_day)
    msg = f'<b>Вы выбрали дату</b>: {selected_day} {keyboard.russian_month_names[selected_month - 1]} {selected_year}\nТеперь выберите время из списка доступных, на которое хотите назначить запись:'
    await callback_query.message.edit_text(msg, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    await Appointment.SET_HOUR_CHOOSE.set()


@dp.callback_query_handler(lambda c: c.data.startswith('hour:'), state=Offline.SET_HOUR_CHOOSE)
async def set_hour_choose_offline(callback_query: CallbackQuery, state: FSMContext):
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
        await callback_query.answer("Ошибка! Не выбран день.")
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
        await callback_query.answer("Ошибка! Неверные данные о времени.")
        return

    await callback_query.message.edit_text(
        '📝 Пожалуйста, кратко опишите <b>симптомы</b> или <b>цель вашей записи</b>. Это поможет нам лучше подготовиться к вашему визиту.',
        reply_markup=keyboard.back_ad,
        parse_mode=ParseMode.HTML
    )
    await state.update_data(appointment_time=appointment_time, selected_hour=selected_hour)
    await Appointment.SET_REASON.set()


@dp.message_handler(lambda message: True, state=Offline.SET_REASON)
async def save_appointment_reason_offline(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        appointment_time = data['appointment_time']
        chat_id = message.chat.id
        user_info = db.get_user_info(chat_id)
        user_id = message.from_user.id
        data['reason'] = message.text.strip()
        name = user_info['name']
        phnum = user_info['phnum']

        appointment_date = appointment_time.strftime(f"%d {keyboard.russian_month_names[appointment_time.month - 1]} %Y года")
        appointment_time_str = appointment_time.strftime("%H:%M")  # Форматируем время как "часы:минуты"

        confirmation_message_offline = (
            f"📝 Подтверждение записи в стоматологию <b>Denta Art</b>\n"
            f"<b>ФИО</b>: {name}\n"
            f"<b>Номер телефона</b>: {phnum}\n"
            f"<b>Дата записи</b>: {appointment_date}\n"
            f"<b>Время записи</b>: {appointment_time_str}\n"
            f"<b>Описание симптомов/цель визита</b>: {data['reason']}\n\n\n"
            f"<i>Пожалуйста, проверьте предоставленную информацию. Если все верно, нажмите '✅ Подтвердить запись'. Если Вы хотите внести изменения, вернитесь назад</i>"
        )

        await message.answer(
            text=confirmation_message_offline,
            reply_markup=keyboard.off_confirm
        )


@dp.callback_query_handler(lambda c: c.data == 'off_confirm', state=Offline.SET_REASON)
async def add_appointment_to_db_offline(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        appointment_time = data['appointment_time']
        selected_hour = data['selected_hour']
        chat_id = callback_query.from_user.id
        user_info = db.get_user_info(chat_id)
        user_id = callback_query.from_user.id
        reason = data['reason']
        name = user_info['name']
        phnum = user_info['phnum']
        appointment_date = appointment_time.strftime(f"%d {keyboard.russian_month_names[appointment_time.month - 1]} %Y года")
        appointment_time_str = appointment_time.strftime("%H:%M")

        db.create_appointment_offline(name, phnum, reason, appointment_time)

        confirmation_message_offline = (
            f"✅ Ваша запись успешно подтверждена!\n"
            f"Ждем вас <b>{appointment_date} в {appointment_time_str}</b>. Если у вас возникнут вопросы или изменения в планах, пожалуйста, свяжитесь с нами заранее. Спасибо за выбор стоматологии '<b>Denta Art</b>'! 🦷\n\n"
            f"Отменить запись можно в главном меню, в разделе 'Личный кабинет' => 'Мои записи'"
        )
        await callback_query.message.edit_text(confirmation_message_offline, parse_mode="HTML")
        await callback_query.message.answer("🛠 Выберите действие:", reply_markup=keyboard.admin_keyboard)
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


async def send_reminders():
    while True:
        current_time = datetime.now()
        upcoming_appointments = db.session.query(Appointment).filter(Appointment.time > current_time).all()

        for appointment in upcoming_appointments:
            time_left = appointment.time - current_time

            if time_left <= timedelta(hours=24):
                notification_text_24h = generate_notification_text(appointment, "24")
                asyncio.create_task(send_notification(appointment.chat_id, notification_text_24h, appointment.time - timedelta(hours=24)))

            if time_left <= timedelta(hours=1):
                notification_text_1h = generate_notification_text(appointment, "1")
                asyncio.create_task(send_notification(appointment.chat_id, notification_text_1h, appointment.time - timedelta(hours=1)))

        await asyncio.sleep(300)

async def send_notification(chat_id, notification_text, notification_time):
    await asyncio.sleep((notification_time - datetime.now()).total_seconds())
    await bot.send_message(chat_id, notification_text, parse_mode="HTML")

def generate_notification_text(appointment, hours_left):
    return (
        f"🆕 У вас запись через {hours_left} {'час' if hours_left == '1' else 'часа'}\n"
        f"<b>ФИО</b>: {appointment.name}\n"
        f"<b>Номер телефона</b>: {appointment.phnum}\n"
        f"<b>Дата записи</b>: {appointment.time.strftime('%d %B %Y года')}\n"
        f"<b>Время записи</b>: {appointment.time.strftime('%H:%M')}\n"
        f"<b>Описание симптомов/цель визита</b>: {appointment.reason}\n\n\n"
        f"<i>Пожалуйста, учтите данную запись в расписании и подготовьте все необходимое для приема.</i>"
    )