from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

from bot.keyboards.main_menu import main_menu

router = Router()


@router.message(CommandStart())
async def start(message: Message):

    await message.answer(
        "Система мониторинга удовлетворенности",
        reply_markup=main_menu()
    )