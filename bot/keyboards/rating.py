from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def rating_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=str(i), callback_data=f"rate_{i}")]
            for i in range(1, 6)
        ]
    )