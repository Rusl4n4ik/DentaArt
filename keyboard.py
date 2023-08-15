from aiogram import types
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


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

user_m = InlineKeyboardMarkup(row_width=1)
user_m.add(types.InlineKeyboardButton("👤 Изменить ФИО", callback_data='ch_name'))
user_m.add(types.InlineKeyboardButton("📞 Изменить номер телефона", callback_data='ch_number'))
user_m.add(back)


admin_keyboard = InlineKeyboardMarkup(row_width=2)
admin_keyboard.add(
    InlineKeyboardButton('Просмотреть всех пользователей', callback_data='admin_show_users'),
    InlineKeyboardButton('📢 Рассылка', callback_data='broadcast'),
    InlineKeyboardButton('💵 Прайс-лист', callback_data='price_list')
)


price_list = InlineKeyboardMarkup(row_width=1)
price_list.add(InlineKeyboardButton('✏ Изменить прайс-лист', callback_data='ch_price'))
price_list.add(InlineKeyboardButton('🔙Назад', callback_data='back_ad'))


def create_price_edit_keyboard():
    list_price = InlineKeyboardMarkup(row_width=1)

    services = [
        '1. Рутинное стоматологическое обследование: $100-$175',
        '2. Профессиональная чистка зубов: $75-$210',
        '3. Скалирование и планирование корней: $150-$320 за квадрант',
        '4. Дентальный герметик: $20-$50 за зуб',
        '5. Зубное или стоматологическое связывание: $100-$550',
        '6. Заполнения зубов: $75-$250',
        '8. Лечение корневого канала: $500-$1,500',
        '8. Стоматологические мосты: $750-$5,000',
        '9. Стоматологические короны: $1,000-$1,500',
        '10. Зубные протезы: $500-$8,000'
    ]

    for service in services:
        button = InlineKeyboardButton(service, callback_data=f"edit_price:{service}")
        list_price.insert(button)

    return list_price