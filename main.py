import asyncio
import calendar
import json
from datetime import datetime
from keyboard import back_markup
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import db,re,keyboard
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import aiogram.utils.markdown as fmt
from fsm import Users, Update, Appointment


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
    prices = db.get_all_prices()
    price_list_text = '💵 Прайс-лист стоматологии "Denta Art":\n'
    for index, price in enumerate(prices, start=1):
        price_list_text += f"{index}. <b>{price.service}:</b> {price.price}\n"
    await message.answer(price_list_text, parse_mode="HTML", reply_markup=keyboard.back_markup)


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
        button_text = f"{day} ✅" if selected_day == day and selected_month == month else str(day)
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
    keyboard.row(InlineKeyboardButton("Назад", callback_data='back'))

    return keyboard


def get_hour_menu(selected_hour=None):
    current_hour = 8
    keyboard = InlineKeyboardMarkup(row_width=3)

    for hour in range(current_hour, 19):
        for minute in range(0, 60, 30):
            formatted_time = f"{hour:02d}:{minute:02d}"
            button_text = f"{formatted_time} ✅" if formatted_time == selected_hour else formatted_time
            button = InlineKeyboardButton(text=button_text, callback_data=f'hour:{formatted_time}')
            keyboard.insert(button)

    return keyboard


@dp.message_handler(text='📅 Запись на прием')
async def start_appointment(message: types.Message):
    current_year = datetime.now().year
    current_month = datetime.now().month
    await message.answer('📅 Чтобы записаться на приëм, выберите удобную для вас дату. Обратите внимание, что прошедшие даты недоступны для выбора.\n'
                         'Воспользуйтесь календарём и для начала выберите дату. <b>После того как отметили дату галочкой, нажмите кнопку</b> "🕘 Выбрать время:"', reply_markup=get_calendar_menu(current_year, current_month))
    await Appointment.SET_DAY.set()


@dp.callback_query_handler(lambda c: c.data.startswith('prev:') or c.data.startswith('next:'),
                           state=Appointment.SET_DAY)
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


@dp.callback_query_handler(lambda c: json.loads(c.data).get('action') == 'day', state=Appointment.SET_DAY)
async def set_day(callback_query: CallbackQuery, state: FSMContext):
    data = json.loads(callback_query.data)
    selected_year = data.get('year')
    selected_month = data.get('month')
    selected_day = data.get('day')
    await state.update_data(selected_day=selected_day)
    await Appointment.SET_HOUR.set()

    # В этом месте также добавьте кнопку "Выбрать время"
    await callback_query.message.edit_reply_markup(
        reply_markup=get_calendar_menu(selected_year, selected_month, selected_day, selected_month))


@dp.callback_query_handler(lambda c: c.data == 'action:choose_time', state=Appointment.SET_HOUR)
async def choose_time(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_hour = data.get('selected_hour')  # Получаем выбранное ранее время
    await callback_query.message.edit_reply_markup(reply_markup=get_hour_menu(selected_hour))
    await Appointment.SET_HOUR.set()


@dp.callback_query_handler(lambda c: c.data.startswith('hour:'), state=Appointment.SET_HOUR)
async def set_hour(callback_query: CallbackQuery, state: FSMContext):
    selected_hour = callback_query.data.split(':')[1]

    data = await state.get_data()
    selected_month = data.get('selected_month')
    selected_day = data.get('selected_day')

    if selected_month is None:
        selected_month = datetime.now().month  # Используем текущий месяц, если не выбран
    if selected_day is None:
        # Обработка ошибки
        await callback_query.answer("Ошибка! Не выбран день.")
        return

    try:
        appointment_time = datetime(
            year=datetime.now().year,
            month=selected_month,
            day=selected_day,
            hour=int(selected_hour)  # Преобразуем строку в целое число
        )
    except TypeError:
        # Обработка ошибки
        await callback_query.answer("Ошибка! Неверные данные о времени.")
        return

    await callback_query.message.answer('📝 Пожалуйста, кратко опишите <b>симптомы</b> или <b>цель вашей записи</b>. Это поможет нам лучше подготовиться к вашему визиту.', reply_markup=back_markup)
    await state.update_data(appointment_time=appointment_time, selected_time=selected_hour)
    await Appointment.SET_REASON.set()


@dp.message_handler(lambda message: True, state=Appointment.SET_REASON)
async def save_appointment_reason(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        appointment_time = data['appointment_time']
        chat_id = message.chat.id
        user_info = db.get_user_info(chat_id)
        user_id = message.from_user.id
        data['reason'] = message.text.strip()
        name = user_info['name']
        phnum = user_info['phnum']

        russian_month_names = [
            'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
            'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
        ]
        appointment_date = appointment_time.strftime(f"%d {russian_month_names[appointment_time.month - 1]} %Y года")
        appointment_time_str = appointment_time.strftime("%H:%M")  # Форматируем время как "часы:минуты"

        confirmation_message = (
            f"📝 Подтверждение записи в стоматологию <b>Denta Art</b>\n"
            f"<b>ФИО</b>: {name}\n"
            f"<b>Номер телефона</b>: {phnum}\n"
            f"<b>Дата записи</b>: {appointment_date}\n"
            f"<b>Время записи</b>: {appointment_time_str}\n"
            f"<b>Описание симптомов/цель визита</b>: {data['reason']}\n\n\n"
            f"<i>Пожалуйста, проверьте предоставленную информацию. Если все верно, нажмите '✅ Подтвердить запись'. Если Вы хотите внести изменения, вернитесь назад</i>"
        )

        await message.answer(
            text=confirmation_message,
            reply_markup=keyboard.app_confirm
        )


@dp.callback_query_handler(lambda c: c.data == 'confirm', state=Appointment.SET_REASON)
async def add_appointment_to_db(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        appointment_time = data['appointment_time']
        selected_hour = data['selected_hour']
        chat_id = callback_query.from_user.id
        user_info = db.get_user_info(chat_id)
        user_id = callback_query.from_user.id
        reason = data['reason']
        name = user_info['name']
        phnum = user_info['phnum']

        russian_month_names = [
            'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
            'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
        ]
        appointment_date = appointment_time.strftime(f"%d {russian_month_names[appointment_time.month - 1]} %Y года")
        appointment_time_str = appointment_time.strftime("%H:%M")

        db.create_appointment(user_id, callback_query.from_user.username, name, phnum, reason, appointment_time)

        confirmation_message = (
            f"✅ Ваша запись успешно подтверждена!\n"
            f"Ждем вас <b>{appointment_date} в {appointment_time_str}</b>. Если у вас возникнут вопросы или изменения в планах, пожалуйста, свяжитесь с нами заранее. Спасибо за выбор стоматологии '<b>Denta Art</b>'! 🦷\n\n"
            f"Отменить запись можно в главном меню, в разделе 'Личный кабинет' => 'Мои записи'"
        )

        await callback_query.message.answer(confirmation_message, parse_mode="HTML")
        await state.finish()



if __name__ == '__main__':
    from aiogram import executor
    from admin import *
    executor.start_polling(dp, skip_updates=True)