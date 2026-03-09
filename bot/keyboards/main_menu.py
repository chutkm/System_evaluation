from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():

    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Оценить обучение")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие в меню ниже ⬇"
    )


# def main_menu():

#     return ReplyKeyboardMarkup(
#         keyboard=[
#             [KeyboardButton(text="Оценить обучение")],
#             [KeyboardButton(text="Главное меню")]
#         ],
#         resize_keyboard=True,
#         input_field_placeholder="Выберите действие в меню ниже ⬇"
#     )