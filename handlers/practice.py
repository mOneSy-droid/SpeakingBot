import random
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

import database as db
import keyboards as kb
from content import STRUCTURES
from gemini_client import check_structure_sentence
from states import PracticeStates
from utils import safe_edit

router = Router()


@router.callback_query(F.data == "menu_practice")
async def start_practice(callback: CallbackQuery, state: FSMContext):
    structure = random.choice(STRUCTURES)
    await state.update_data(pattern=structure["pattern"])
    await state.set_state(PracticeStates.waiting_for_sentence)

    text = (
        "🗣 <b>Gap tuzilishi mashqi</b>\n\n"
        f"Pattern: <b>{structure['pattern']}</b>\n"
        f"📝 {structure['explanation']}\n"
        f"Namuna: <i>{structure['example']}</i>\n\n"
        "Endi shu pattern asosida o'z jumlangizni yozing (matn xabar sifatida yuboring):"
    )
    await safe_edit(callback.message, text, reply_markup=kb.back_to_menu())
    await callback.answer()


@router.message(PracticeStates.waiting_for_sentence)
async def receive_sentence(message: Message, state: FSMContext):
    data = await state.get_data()
    pattern = data.get("pattern", "")

    thinking = await message.answer("⏳ Tekshirilmoqda...")
    feedback = await check_structure_sentence(pattern, message.text)
    await db.log_practice(message.from_user.id, "structure")

    await safe_edit(thinking, f"📋 <b>Feedback:</b>\n\n{feedback}", reply_markup=kb.practice_keyboard())
    await state.clear()
