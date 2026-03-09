from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def days_keyboard(days):

    keyboard = []

    for day in days:
        keyboard.append([
            InlineKeyboardButton(
                text=day,
                callback_data=f"day_{day}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            text="🏠 В меню",
            callback_data="menu"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)