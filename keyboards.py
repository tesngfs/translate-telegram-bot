from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

url = 'https://teletype.in/@naumov_glav/lS5Pfwf0q51' # link to the countries
url_admin = 'https://t.me/naumov_glav' # link to admin
url_link = 'https://t.me/translatebo_bot?startgroup=start' # add to your chat

def get_start_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Изменить язык', callback_data='value_transalate'),
            InlineKeyboardButton(text='Список языков', url=url)
        ],
        [
            InlineKeyboardButton(text='Администратор', url=url_admin)
        ],
        [
            InlineKeyboardButton(text='Добавить в чат', url=url_link)
        ]
    ])

def get_check_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Подписаться', url=url_admin),
            InlineKeyboardButton(text='Проверить', callback_data='check'),
        ]
    ])

def get_language_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Список языков', url=url)
        ]
    ])


def get_new_language_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Перевести', callback_data = 'check')
        ]
    ])

