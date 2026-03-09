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

    return InlineKeyboardMarkup(inline_keyboard=keyboard)