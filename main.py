import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove

import db,re,keyboard
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import aiogram.utils.markdown as fmt
from fsm import Users, Update


API_TOKEN = '6494026269:AAFptKHhMWHC2vCbUBNfNwrij-dDHANbkdw'

bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())
tmp = {}


@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message, state: FSMContext):
    exist_user = db.check_existing(message.chat.id)
    if not exist_user:
        await message.answer('👋Добро пожаловать в телеграм-бот стоматологии <b>Denta Art</b>\n <b><i>Выберите язык интерфейса:</i></b>\n➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n 👋<b>Denta Art</b> stomatologiyasi telegram- botiga xush kelibsiz\n <b><i>Interfeys tilini tanlang:</i></b>', reply_markup=keyboard.languages)

        @dp.callback_query_handler(lambda c: c.data == 'ru')
        async def process_callback_ru(callback_query: types.CallbackQuery):
            await bot.send_message(callback_query.from_user.id, "<b>Заполнение данных о пациенте 1/2📝</b>\nПожалуйста, введите ваше полное имя <b>(фамилия Имя Отчество)</b>")
            user_id = message.from_user.id
            await Users.Name.set()

        @dp.callback_query_handler(lambda c: c.data == 'ozb')
        async def process_callback_ozb(callback_query: types.CallbackQuery):
            await bot.answer_callback_query(callback_query.id, text="Siz O'zbek tilini tanladingiz.")
            await bot.send_message(callback_query.from_user.id, "Siz O'zbek tilini tanladingiz.")

    else:
        await message.answer("👋Добро пожаловать в телеграм-ботстоматологии <b>Denta Art</b>! Здесь Вы можете записаться на прием к стоматологу. Выберите интересующий вас пункт в меню ниже. "
                             "❓ Если у вас возникли вопросы по работе с ботом, ознакомьтесь с инструкцией ниже или свяжитесь с нами по телефону <u>+998902706390</u>.", reply_markup=keyboard.start_m)


@dp.message_handler(state=Users.Name)
async def phnum(message: types.Message, state: FSMContext):
    name_input = message.text
    lastname_name_surname = name_input.split()

    if len(lastname_name_surname) == 3:
        lastname, name, surname = lastname_name_surname
        if re.match(r'^[А-ЯЁа-яё]+\s[А-ЯЁа-яё]+\s[А-ЯЁа-яё]+$', name_input):
            lastname = lastname.capitalize()
            name = name.capitalize()
            surname = surname.capitalize()
            lastname_name_surname = lastname + ' ' + name + ' ' + surname
            await state.update_data(name=lastname_name_surname)
            await message.answer(
                '<b>Заполнение данных о пациенте 2/2📝</b>\n 📞Теперь, пожалуйста, введите ваш номер телефона. Мы используем его только для связи с вами по вопросам записи.\n<b>Формат:</b> <u>+998902706390</u>')
            await Users.Phnum.set()
        else:
            await message.answer(
                "⚠️ Кажемся, вы ввели ФИО в неправильном формате. Пожалуйста, убедитесь, что вы ввели ваше полное имя в формате 'Фамилия Имя Отчество. Попробуйте еще раз:")
    else:
        await message.answer('⚠️ Введите ФИО в одной строке, разделенные одним пробелом.')


@dp.message_handler(state=Users.Phnum)
async def addphnum(message: types.Message, state: FSMContext):
    phnum = message.text
    if re.match(r'^\+998\d{9}$', phnum):
        await state.update_data(phnum=phnum)
        data = await state.get_data()
        db.add_user(message.chat.id, first_name=message.from_user.first_name, username=message.from_user.username, name=data['name'], phnum=data['phnum'])
        await state.finish()
        await message.answer(
            "👋Добро пожаловать в телеграм-ботстоматологии <b>Denta Art</b>! Здесь Вы можете записаться на прием к стоматологу. Выберите интересующий вас пункт в меню ниже. "
            "❓ Если у вас возникли вопросы по работе с ботом, ознакомьтесь с инструкцией ниже или свяжитесь с нами по телефону <u>+998902706390</u>.", reply_markup=keyboard.start_m)

    else:
        await message.answer('⚠️ Неправильный формат номера телефона. Введите номер в формате +998XXXXXXXXX.')


@dp.message_handler(text='🏥 О Клинике')
async def about(message: types.Message):
    loading_msg = await message.answer('Загрузка информации..', reply_markup=types.ReplyKeyboardRemove())
    await asyncio.sleep(1)
    await message.answer('🏥 <b>Denta Art</b> - это современная стоматологическая клиника,'
                         'предоставляющая полный спектр услуг.\n<b>Наши адрес и контакты:</b> <i>г. Самарканд, ул. Фитрат, 47,</i> <u>+998902706390</u>.\n'
                         '<b>Директор:</b> Садуллаев Анвар\n'
                         '<b>Рабочее время:</b> C 8:00 до 18:00', reply_markup=keyboard.back_markup)


@dp.message_handler(text='💵 Прайс-лист')
async def price(message: types.Message):
    loading_msg = await message.answer('Загрузка прайс-листа...', reply_markup=types.ReplyKeyboardRemove())
    await asyncio.sleep(1)
    await bot.delete_message(chat_id=message.chat.id, message_id=loading_msg.message_id)
    await message.answer('💵 Прайс-лист стоматологии "Denta Art":\n'
                         '1. <b>Рутинное стоматологическое обследование:</b> $100-$175\n'
                         '2. <b>Профессиональная чистка зубов:</b> $75-$210\n'
                         '3. <b>Скалирование и планирование корней:</b> $150-$320 за квадрант\n'
                         '4. <b>Дентальный герметик:</b> $20-$50 за зуб\n'
                         '5. <b>Зубное или стоматологическое связывание:</b> $100-$550\n'
                         '6. <b>Заполнения зубов:</b> $75-$250\n'
                         '8. <b>Лечение корневого канала:</b> $500-$1,500\n'
                         '8. <b>Стоматологические мосты:</b> $750-$5,000\n'
                         '9. <b>Стоматологические короны:</b> $1,000-$1,500\n'
                         '10. <b>Зубные протезы:</b> $500-$8,000\n', reply_markup=keyboard.back_markup)


@dp.message_handler(text='👤 Личный кабинет')
async def user_info(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        chat_id = message.chat.id
        user_info = db.get_user_info(chat_id)
        name = user_info['name']
        num = user_info['phnum']
        loading_msg = await message.answer('Загрузка...', reply_markup=types.ReplyKeyboardRemove())
        await asyncio.sleep(1)
        await bot.delete_message(chat_id=message.chat.id, message_id=loading_msg.message_id)
        await message.answer(f'<b>Ваше ФИО:</b> {name}\n<b>Ваш номер телефона:</b> {num}\n'
                             '👤 В личном кабинете Вы сможете поменять данные о пациенте <b>(О себе)</b> или же просмотреть свои записи по кнопке "✏Мои записи"\n\n\n'
                             ' <b><i>Выберите пункт, который хотите поменять:</i></b>\nЕсли нечего менять, вернитесь на предыдущую страницу, используя кнопку "🔙Назад"', reply_markup=keyboard.user_m)


@dp.callback_query_handler(lambda c: c.data == 'back', state='*')
async def go_back(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.finish()
    await callback.message.answer("👋Добро пожаловать в телеграм-ботстоматологии <b>Denta Art</b>! Здесь Вы можете записаться на прием к стоматологу. Выберите интересующий вас пункт в меню ниже. "
                             "❓ Если у вас возникли вопросы по работе с ботом, ознакомьтесь с инструкцией ниже или свяжитесь с нами по телефону <u>+998902706390</u>.", reply_markup=keyboard.start_m)


@dp.callback_query_handler(lambda c: c.data == 'ch_name')
async def change_name(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer("📝 Введите ваше новое ФИО в формате 'Фамилия Имя Отчество'", reply_markup=types.ReplyKeyboardRemove())
    await Update.Name.set()


@dp.callback_query_handler(lambda c: c.data == 'ch_number')
async def change_number(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer("Введите ваш новый номер в формате '+998XXXXXXXXX'.", reply_markup=types.ReplyKeyboardRemove())
    await Update.Phnum.set()


@dp.message_handler(state=Update.Name)
async def set_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        chat_id = message.chat.id
        new_name = message.text
        if re.match(r'^[А-ЯЁа-яё]+\s[А-ЯЁа-яё]+\s[А-ЯЁа-яё]+$', new_name):
            old_data = await state.get_data()
            db.update_user(chat_id, name=new_name, phnum=old_data.get('phnum'))
            await state.finish()
            await message.answer('✅ <i>Ваше ФИО успешно обновлено!</i>', reply_markup=keyboard.back_markup)
        else:
            await message.answer("⚠️ Кажется, вы ввели ФИО в неправильном формате. Пожалуйста, убедитесь, что вы ввели ваше полное имя в формате 'Фамилия Имя Отчество'. Попробуйте еще раз:")


@dp.message_handler(state=Update.Phnum)
async def set_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        chat_id = message.chat.id
        new_number = message.text
        if re.match(r'^\+998\d{9}$', new_number):
            old_data = await state.get_data()
            db.update_user(chat_id, name=old_data.get('name'), phnum=new_number)
            await state.finish()
            await message.answer('✅ <i>Ваш номер телефона успешно обновлен!</i>', reply_markup=keyboard.back_markup)
        else:
            await message.answer("⚠️ <i>Введенный номер телефона кажется некорректным. Пожалуйста, убедитесь, что вы ввели номер в формате </i> '+998XXXXXXXXX'\n<b>Например,<u>'+998902706390'.</u> Попробуйте еще раз: </b>")


if __name__ == '__main__':
    from aiogram import executor
    from admin import *  # Импортируйте модуль с админ-панелью
    executor.start_polling(dp, skip_updates=True)