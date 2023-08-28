import calendar
from datetime import datetime
import db
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.callback_data import CallbackData
from locales import get_text

#################################################################################
languages = types.InlineKeyboardMarkup(row_width=1)
languages.add(types.InlineKeyboardButton("🇷🇺 Русский", callback_data='ru'))
languages.add(types.InlineKeyboardButton("🇺🇿 O'zbek", callback_data='uz'))

ch_language = types.InlineKeyboardMarkup(row_width=1)
ch_language.add(types.InlineKeyboardButton("🇷🇺 Русский", callback_data='rus'))
ch_language.add(types.InlineKeyboardButton("🇺🇿 O'zbek", callback_data='uzb'))


def get_start_keyboard(lang_code):
    start_m = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    start_btn1, start_btn2 = map(lambda key: get_text(lang_code, key), ['start_btn1', 'start_btn2'])
    start_btn3 = get_text(lang_code, 'start_btn3')
    start_btn4 = get_text(lang_code, 'start_btn4')
    start_m.row(start_btn1, start_btn2)
    start_m.add(start_btn3, start_btn4)
    return start_m


def get_back_keyboard(lang):
    back_button = InlineKeyboardButton(get_text(lang, 'back'), callback_data='back')
    back_markup = InlineKeyboardMarkup().add(back_button)
    return back_markup


def get_app_confirm_keyboard(lang):
    app_confirm = InlineKeyboardMarkup(row_width=1)
    confirm_button = InlineKeyboardButton(get_text(lang, 'confirm'), callback_data='confirm')
    back = InlineKeyboardButton(get_text(lang, 'back'), callback_data='back')
    app_confirm.add(confirm_button, back)
    return app_confirm


def get_del_confirm_keyboard(lang):
    del_confirm_m = InlineKeyboardMarkup(row_width=1)
    delete_button = InlineKeyboardButton(get_text(lang, 'yes'), callback_data='del_confirm')
    back = InlineKeyboardButton(get_text(lang, 'back'), callback_data='back')
    del_confirm_m.add(delete_button, back)
    return del_confirm_m


def get_cancel_keyboard(lang):
    cancel_m = InlineKeyboardMarkup(row_width=1)
    cancel_button = InlineKeyboardButton(get_text(lang, 'cancel'), callback_data='cancel')
    back = InlineKeyboardButton(get_text(lang, 'back'), callback_data='back')
    cancel_m.add(cancel_button, back)
    return cancel_m

#####################################################################


def get_user_keyboard(lang):
    user_m = InlineKeyboardMarkup(row_width=1)
    user_m.add(InlineKeyboardButton(get_text(lang, 'app_my'), callback_data='my_app'))
    user_m.add(InlineKeyboardButton(get_text(lang, 'change_fio'), callback_data='ch_name'))
    user_m.add(InlineKeyboardButton(get_text(lang, 'change_phum'), callback_data='ch_number'))
    user_m.add(InlineKeyboardButton(get_text(lang, 'change_lang'), callback_data='ch_lang'))
    user_m.add(InlineKeyboardButton(get_text(lang, 'back'), callback_data='back'))
    return user_m
#####################################################################


back_ad = InlineKeyboardButton('🔙Назад', callback_data='back_ad')
back_admin = types.InlineKeyboardMarkup().add(back_ad)

off_confirm = InlineKeyboardMarkup(row_width=1)
confirm = InlineKeyboardButton('✅ Подтвердить запись', callback_data='off_confirm')
off_confirm.add(confirm)
off_confirm.add(back_ad)


admin_keyboard = InlineKeyboardMarkup(row_width=2)
admin_keyboard.add(InlineKeyboardButton('Просмотреть всех пользователей', callback_data='admin_show_users'))
admin_keyboard.add(InlineKeyboardButton('✍ Офлайн запись', callback_data='offline_appointment'))
admin_keyboard.add(InlineKeyboardButton('📢 Рассылка', callback_data='broadcast'))
admin_keyboard.add(InlineKeyboardButton('💵 Прайс-лист', callback_data='price_list'))
admin_keyboard.add(InlineKeyboardButton('📝 Просмотреть записи', callback_data='view_app'))
admin_keyboard.add(InlineKeyboardButton('📝 Календарь', callback_data='calendar'))
admin_keyboard.add(InlineKeyboardButton('💵 Добавить услугу', callback_data='add_service'))
#####################################################################

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
#####################################################################


russian_month_names = [
            'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
            'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
        ]

uzb_month_names = [
             "yanvar", "fevral", "mart", "aprel", "may", "iyun",
             "Iyul", "avgust", "sentyabr", "oktyabr", "noyabr", "dekabr"
         ]
#####################################################################
