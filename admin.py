from aiogram import types

from aiogram.dispatcher.filters import Text, state
from aiogram.types import ReplyKeyboardRemove, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from fsm import Admins
from main import dp, bot
import db, keyboard
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
    await callback.answer()
    await state.finish()
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
        await bot.send_message(callback.from_user.id, f"Список пользователей:\n{user_list}", reply_markup=reply_markup)
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

    await callback.message.delete()
    await callback.answer()
    await bot.send_message(callback.from_user.id, f"Список пользователей:\n{user_list}", reply_markup=reply_markup)
    await callback.message.delete()


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

    if appointments:
        message = "Список всех записей:\n\n"
        for idx, appointment in enumerate(appointments, start=1):
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
    else:
        message = "Нет записей."

    await callback_query.message.edit_text(message, reply_markup=keyboard.back_admin, parse_mode='HTML')

# @dp.callback_query_handler(text="ch_price")
# async def change_price_list(callback_query: CallbackQuery, state: FSMContext):
#     await callback_query.answer()
#
#     prices = db.get_all_prices()  # Получите список цен и услуг из базы данных
#     await callback_query.message.answer("Выберите услугу, для которой вы хотите изменить прайс:",
#                                         reply_markup=keyboard.create_price_edit_keyboard(prices))
#     await Admins.EditPrice.set()
#
#
# @dp.callback_query_handler(price_edit_callback.filter(), state=Admins.EditPrice)
# async def edit_price(callback_query: CallbackQuery, state: FSMContext, callback_data: dict):
#     await callback_query.answer()
#     service_index = int(callback_data["service_index"])
#     selected_price = db.get_price_by_index(service_index)  # Замените на метод получения цены из базы данных по индексу
#     await callback_query.message.answer(f"Вы редактируете прайс для услуги {selected_price.service}. Введите новый прайс или оставьте пустым, чтобы не изменять:")
#     await Admins.EditPriceAmount.set()
#     async with state.proxy() as data:
#         data["editing_service"] = selected_price.service
#
#
#
# @dp.message_handler(state=Admins.EditPriceAmount)
# async def save_new_price_or_service_name(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         editing_service = data["editing_service"]
#
#     new_price_or_service_name = message.text.strip()
#
#     if new_price_or_service_name:
#         db.update_service_price(editing_service, new_price_or_service_name)
#         await message.answer("Изменения сохранены.")
#     else:
#         await message.answer("Изменения не сохранены.")
#
#     await state.finish()






# price_edit_callback = CallbackData("edit_price", "service")


# @dp.callback_query_handler(text="ch_price")
# async def change_price_list(callback_query: CallbackQuery, state: FSMContext):
#     await callback_query.answer()
#     await callback_query.message.answer("Выберите услугу, для которой вы хотите изменить прайс:", reply_markup=keyboard.create_price_edit_keyboard(price))
#     await Admins.EditPrice.set()
#     await state.update_data(editing_price=True)
#
#
# @dp.callback_query_handler(price_edit_callback.filter(), state=Admins.EditPrice)
# async def edit_price(callback_query: CallbackQuery, state: FSMContext, callback_data: dict):
#     await callback_query.answer()
#     service_number = callback_data["service"]
#     await callback_query.message.answer(f"Вы редактируете прайс для услуги {service_number}. Введите новый прайс:")
#     await Admins.EditPriceAmount.set()
#     async with state.proxy() as data:
#         data["editing_service"] = service_number
#
#
# @dp.message_handler(lambda message: message.text.isdigit(), state=Admins.EditPriceAmount)
# async def save_new_price(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         editing_service = data["editing_service"]
#     new_price = int(message.text)
#     db.update_price(editing_service, new_price)
#     await message.answer("Новый прайс успешно сохранен.")
#     await state.finish()