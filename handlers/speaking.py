import os
import random
import time

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

import database as db
import keyboards as kb
from content import SPEAKING_PROMPTS
from gemini_client import evaluate_speaking
from transcription import transcribe
from states import SpeakingStates
from utils import safe_edit
from filler_analyzer import count_filler_words, get_filler_feedback

router = Router()


@router.callback_query(F.data == "menu_speaking")
async def start_speaking(callback: CallbackQuery, state: FSMContext):
    question = random.choice(SPEAKING_PROMPTS)
    await state.update_data(speaking_question=question)
    await state.set_state(SpeakingStates.waiting_for_voice)

    text = (
        "🎤 <b>Speaking mashqi</b>\n\n"
        f"Savol: <b>{question}</b>\n\n"
        "Endi 🎤 ovozli xabar (voice message) orqali ingliz tilida javob bering. "
        "Tabiiy tezlikda gapiring, xuddi haqiqiy uchrashuvdagidek."
    )
    await safe_edit(callback.message, text, reply_markup=kb.back_to_menu())
    await callback.answer()


@router.message(SpeakingStates.waiting_for_voice, F.voice)
async def receive_voice(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    question = data.get("speaking_question", "")

    thinking = await message.answer("⏳ Ovoz matga aylantirilmoqda (birinchi marta biroz sekin bo'lishi mumkin)...")

    file = await bot.get_file(message.voice.file_id)
    local_path = f"/tmp/voice_{message.from_user.id}_{int(time.time())}.ogg"
    await bot.download_file(file.file_path, local_path)

    try:
        text, duration = transcribe(local_path)
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)

    if not text:
        await safe_edit(thinking, 
            "Ovozni tanimadim 😕 Iltimos, aniqroq va sokinroq joyda qayta gapirib ko'ring.",
            reply_markup=kb.back_to_menu(),
        )
        await state.clear()
        return

    word_count = len(text.split())
    wpm = round(word_count / (duration / 60), 1) if duration > 0 else 0

    await safe_edit(thinking, f"📝 Eshitilgan matn:\n<i>{text}</i>\n\n⏳ Baholanmoqda...")

    feedback = await evaluate_speaking(question, text, wpm, duration)
    
    # Analyze filler words
    filler_analysis = count_filler_words(text)
    filler_feedback = get_filler_feedback(filler_analysis)
    
    # Calculate quality score (0-100)
    quality_score = max(0, 100 - (filler_analysis["percentage"] * 5) - (max(0, wpm - 150) / 5))
    quality_score = min(100, int(quality_score))
    
    # Save voice recording to database
    await db.save_voice_recording(
        telegram_id=message.from_user.id,
        question=question,
        transcript=text,
        file_path="",  # Can store file if needed
        wpm=wpm,
        filler_count=filler_analysis["total"],
        filler_list=filler_analysis["list"],
        feedback=feedback,
        quality_score=quality_score,
    )
    
    await db.log_practice(message.from_user.id, "speaking")
    
    # Update last practice date
    from datetime import datetime, timezone
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    await db.set_last_practice_date(message.from_user.id, today)

    result_text = (
        f"📝 <b>Transkripsiya:</b>\n<i>{text}</i>\n\n"
        f"⏱ Davomiylik: {duration:.0f}s | Tezlik: {wpm} so'z/daqiqa | ⭐ Sifat: {quality_score}%\n\n"
        f"📋 <b>Baho:</b>\n{feedback}\n\n"
        f"🗣 <b>Filler so'zlar:</b>\n{filler_feedback}"
    )
    await safe_edit(thinking, result_text, reply_markup=kb.speaking_keyboard())
    await state.clear()


@router.message(SpeakingStates.waiting_for_voice)
async def wrong_content_type(message: Message):
    await message.answer("Iltimos, 🎤 ovozli xabar (voice message) yuboring, oddiy matn emas.")
