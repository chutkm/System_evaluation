from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

from bot.keyboards.main_menu import main_menu

router = Router()


from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart

@router.message(CommandStart())
async def start(message: Message):

    photo = FSInputFile(
        r"D:\VSCProjects\system_evaluation\System_evaluation\mstuca.jpg"
    )

    text = (
        "Здравствуйте! 👋\n\n"
        "Вас приветствует система оценки учебного процесса.\n\n"
        "Ваше мнение очень важно для нас — оно помогает "
        "улучшать качество обучения, организацию занятий "
        "и взаимодействие со студентами.\n\n"
        "Оценка занимает всего несколько секунд, "
        "но может значительно повлиять на развитие образовательного процесса.\n\n"
        "Спасибо за участие! 💙"
    )

    await message.answer_photo(
        photo=photo,
        caption=text,
        reply_markup=main_menu()
    )