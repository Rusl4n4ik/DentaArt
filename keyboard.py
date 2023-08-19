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
    InlineKeyboardButton('📝 Просмотреть записи', callback_data='view_app')
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


