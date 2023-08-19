import calendar
from datetime import datetime

from aiogram import types
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

languages = types.InlineKeyboardMarkup(row_width=1)
languages.add(types.InlineKeyboardButton("🇷🇺 Русский", callback_data='ru'))
languages.add(types.InlineKeyboardButton("🇺🇿 O'zbek", callback_data='ozb'))


start_m = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
start_btn1 = ['🏥 О Клинике', '💵 Прайс-лист']
start_btn2= ['📅 Запись на прием']
start_btn3= ['👤 Личный кабинет']
start_m.add(*start_btn1)
start_m.add(*start_btn2)
start_m.add(*start_btn3)


back = InlineKeyboardButton('🔙Назад', callback_data='back')
back_markup = types.InlineKeyboardMarkup().add(back)

back_ad = InlineKeyboardButton('🔙Назад', callback_data='back_ad')
back_admin = types.InlineKeyboardMarkup().add(back_ad)

app_confirm = InlineKeyboardMarkup(row_width=1)
confirm = InlineKeyboardButton('✅ Подтвердить запись', callback_data='confirm')
app_confirm.add(confirm)
app_confirm.add(back)


del_confirm = InlineKeyboardMarkup(row_width=1)
delete = InlineKeyboardButton('✅ Да', callback_data='del_confirm')
del_confirm.add(delete)
del_confirm.add(back)


cancel_m = InlineKeyboardMarkup(row_width=1)
cancel = InlineKeyboardButton('❌ Отменить запись', callback_data='cancel')
cancel_m.add(cancel)
cancel_m.add(back)

user_m = InlineKeyboardMarkup(row_width=1)
user_m.add(types.InlineKeyboardButton("✏ Мои записи", callback_data='my_app'))
user_m.add(types.InlineKeyboardButton("👤 Изменить ФИО", callback_data='ch_name'))
user_m.add(types.InlineKeyboardButton("📞 Изменить номер телефона", callback_data='ch_number'))
user_m.add(back)


admin_keyboard = InlineKeyboardMarkup(row_width=2)
admin_keyboard.add(
    InlineKeyboardButton('Просмотреть всех пользователей', callback_data='admin_show_users'),
    InlineKeyboardButton('📢 Рассылка', callback_data='broadcast'),
    InlineKeyboardButton('💵 Прайс-лист', callback_data='price_list'),
    InlineKeyboardButton('📝 Просмотреть записи', callback_data='view_app'),
    InlineKeyboardButton('📝 Календарь', callback_data='calendar')
)


broadcast_option_menu = InlineKeyboardMarkup(row_width=1)
broadcast_option_menu.add(
    InlineKeyboardButton(text='📣 Рассылка всем', callback_data='broadcast_all'),
    InlineKeyboardButton(text='📣 Рассылка пользователям с записями', callback_data='broadcast_with_appointments'),
    InlineKeyboardButton(text='🔙Назад', callback_data='back_ad')
)


price_list = InlineKeyboardMarkup(row_width=1)
price_list.add(InlineKeyboardButton('✏ Изменить прайс-лист', callback_data='ch_price'))
price_list.add(InlineKeyboardButton('🔙Назад', callback_data='back_ad'))


price_edit_callback = CallbackData("price_edit", "service_index")


def create_price_edit_keyboard(prices):
    buttons = [InlineKeyboardButton(f'{index + 1}. {price.service}', callback_data=price_edit_callback.new(service_index=index)) for index, price in enumerate(prices)]
    return InlineKeyboardMarkup(inline_keyboard=[[button] for button in buttons])


russian_month_names = [
            'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
            'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
        ]


def get_admin_calendar_menu(year, month, selected_day=None, selected_month=None):
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
                {'action': 'admin_day', 'year': year, 'month': month, 'day': day}))
            day_row.append(button)
        else:
            button_text = f"{day} ❌" if selected_day == day and selected_month == month else f"{day} ❌"
            button = InlineKeyboardButton(text=button_text, callback_data=json.dumps(
                {'action': 'admin_day', 'year': year, 'month': month, 'day': day}))
            day_row.append(button)

        if len(day_row) == 5:
            day_buttons.append(day_row)
            day_row = []

    if day_row:
        day_buttons.append(day_row)

    for row in day_buttons:
        keyboard.row(*row)

    keyboard.row(InlineKeyboardButton("🔙Назад", callback_data='admin_back'))

    return keyboard


def get_admin_hour_menu(year, month, day, selected_hour=None):
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
                button = InlineKeyboardButton(text=button_text, callback_data=f'admin_hour:{formatted_time}')
                keyboard.insert(button)
            else:
                button_text = f"{formatted_time} ❌" if formatted_time == selected_hour else formatted_time
                button = InlineKeyboardButton(text=button_text, callback_data=f'admin_hour:{formatted_time}')
                keyboard.insert(button)

    back_button = InlineKeyboardButton("🔙Назад", callback_data='admin_hour_back')
    keyboard.row(back_button)

    return keyboard



# current_prices = {
#     'Рутинное стоматологическое обследование': '100-$175',
#     'Профессиональная чистка зубов': '$75-$210',
#     'Скалирование и планирование корней': '$150-$320 за квадрант',
#     'Дентальный герметик': '$20-$50 за зуб',
#     'Зубное или стоматологическое связывание': '$100-$550',
#     'Заполнения зубов': '$75-$250',
#     'Лечение корневого канала': '$500-$1,500',
#     'Стоматологические мосты': '$750-$5,000',
#     'Стоматологические короны': '$1,000-$1,500',
#     'Зубные протезы': '$500-$8,000'
# }
#
#
# def create_price_edit_keyboard():
#     buttons = [
#         InlineKeyboardButton(f'{service}: {current_prices.get(service, "N/A")}', callback_data=f"edit_price:{service}")
#         for service in current_prices
#     ]
#     return InlineKeyboardMarkup(inline_keyboard=[buttons])


