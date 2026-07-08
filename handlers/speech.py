from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

import database as db
import keyboards as kb
from gemini_client import review_speech
from states import SpeechStates
from utils import safe_edit

router = Router()


@router.callback_query(F.data == "menu_speech")
async def start_speech_review(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SpeechStates.waiting_for_draft)
    text = (
        "✍️ <b>Speech tuzatish</b>\n\n"
        "Speech matningizning bir qismini (yoki hammasini) yuboring — "
        "grammatikasini tuzataman va yaxshiroq variant taklif qilaman.\n\n"
        "Ingliz tilida yozing, uzun bo'lsa ham bo'ladi."
    )
    await safe_edit(callback.message, text, reply_markup=kb.back_to_menu())
    await callback.answer()


@router.message(SpeechStates.waiting_for_draft)
async def receive_draft(message: Message, state: FSMContext):
    thinking = await message.answer("⏳ Tekshirilmoqda, biroz kuting...")
    feedback = await review_speech(message.text)
    await db.log_practice(message.from_user.id, "speech")

    await safe_edit(thinking, feedback, reply_markup=kb.back_to_menu())
    await state.clear()
