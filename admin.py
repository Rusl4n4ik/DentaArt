from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove, CallbackQuery
from fsm import Admins
from main import dp, bot
import db, keyboard
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from fsm import Users, Update


@dp.message_handler(commands=['admin'])
async def admin_panel(message: types.Message):
    db.add_admin(message.chat.id, message.from_user.first_name, message.from_user.username)
    await message.answer("🛠 Выберите действие:", reply_markup=keyboard.admin_keyboard)


@dp.callback_query_handler(lambda c: c.data == 'back_ad', state='*')
async def go_back(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.finish()
    await callback.message.answer("🛠 Выберите действие:", reply_markup=keyboard.admin_keyboard)


@dp.callback_query_handler(text="broadcast")
async def broadcast_button_handler(callback_query: CallbackQuery, state: FSMContext):
    chat_id = callback_query.from_user.id
    if db.is_admin(chat_id):
        await callback_query.answer()
        await callback_query.message.answer("Введите текст сообщения для рассылки:", reply_markup=keyboard.back_admin)
        await Admins.Broadcast.set()
    else:
        await callback_query.answer("Вы не являетесь администратором.")


@dp.message_handler(commands=("cancel"), state=Admins.Broadcast)
@dp.message_handler(Text(equals="/cancel", ignore_case=True), state=Admins.Broadcast)
async def cancel_broadcast(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Рассылка отменена.", reply_markup=keyboard.back_admin)


@dp.message_handler(state=Admins.Broadcast)
async def process_broadcast(message: types.Message, state: FSMContext):
    users = db.get_all_users()
    total_users = len(users)
    if total_users == 1:
        await bot.send_message(users[0]['chat_id'], message.text)
        await state.finish()
        await message.answer(f"Сообщение успешно отправлено 1 пользователю.", reply_markup=keyboard.back_admin)
    elif total_users > 1:
        for user in users:
            chat_id = user['chat_id']
            await bot.send_message(chat_id, message.text)
        await state.finish()
        await message.answer(f"Сообщение успешно отправлено {total_users} пользователям.", reply_markup=keyboard.back_admin)
    else:
        await state.finish()
        await message.answer("Нет доступных пользователей для рассылки.", reply_markup=keyboard.back_admin)


@dp.callback_query_handler(lambda c: c.data == 'admin_show_users')
async def admin_show_users(callback: types.CallbackQuery):
    users = db.get_all_users()
    if users:
        user_list = "\n".join([f"<b>{user['name']}:</b> {user['phnum']}" for user in users])
        await callback.answer()
        await bot.send_message(callback.from_user.id, f"Список пользователей:\n{user_list}", reply_markup=keyboard.back_admin)
    else:
        await callback.answer("Нет зарегистрированных пользователей.")


@dp.callback_query_handler(text="price_list")
async def show_price_list(callback_query: CallbackQuery):
    await callback_query.answer()

    price_list_text = (
        '💵 Прайс-лист стоматологии "Denta Art":\n'
        '1. Рутинное стоматологическое обследование: $100-$175\n'
        '2. Профессиональная чистка зубов: $75-$210\n'
        '3. Скалирование и планирование корней: $150-$320 за квадрант\n'
        '4. Дентальный герметик: $20-$50 за зуб\n'
        '5. Зубное или стоматологическое связывание: $100-$550\n'
        '6. Заполнения зубов: $75-$250\n'
        '8. Лечение корневого канала: $500-$1,500\n'
        '8. Стоматологические мосты: $750-$5,000\n'
        '9. Стоматологические короны: $1,000-$1,500\n'
        '10. Зубные протезы: $500-$8,000'
    )
    await callback_query.message.answer(price_list_text, reply_markup=keyboard.price_list)
