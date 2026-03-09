from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def rating_keyboard():

    keyboard = []

    for i in range(1, 6):

        keyboard.append([
            InlineKeyboardButton(
                text="⭐" * i,
                callback_data=f"rate_{i}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(text="⬅ Назад", callback_data="back_lesson")
    ])

    keyboard.append([
        InlineKeyboardButton(text="🏠 В меню", callback_data="menu")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)