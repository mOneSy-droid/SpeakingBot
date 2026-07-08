from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

import database as db
import keyboards as kb
from utils import safe_edit

router = Router()

WELCOME = (
    "Assalomu alaykum! 👋\n\n"
    "Men sizga Malaysia universiteti bilan bo'ladigan speech'ga tayyorlanishda yordam beraman.\n\n"
    "1 oylik dastur 4 haftaga bo'lingan:\n"
    "1-hafta: Tanishtiruv va partnership so'zlari\n"
    "2-hafta: Ta'lim tizimi so'zlari\n"
    "3-hafta: Biznes/muzokara so'zlari\n"
    "4-hafta: Yakuniy nutq va xulosa\n\n"
    "Quyidagi menyudan boshlang:"
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await db.ensure_user(message.from_user.id, message.from_user.username)
    await message.answer(WELCOME, reply_markup=kb.main_menu())


@router.callback_query(F.data == "menu_back")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_edit(callback.message, "Menyu:", reply_markup=kb.main_menu())
    await callback.answer()
