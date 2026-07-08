import os
import re
import time

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

import database as db
import keyboards as kb
from content import QA_TOPIC_HINT
from gemini_client import generate_qa_questions, evaluate_qa_answer, evaluate_speaking
from transcription import transcribe
from states import QAStates
from utils import safe_edit

router = Router()

_LEADING_NUMBER = re.compile(r"^\s*\d+[\.\)]\s*")


def parse_questions(raw: str) -> list[str]:
    lines = [line.strip() for line in raw.split("\n") if line.strip()]
    questions = [_LEADING_NUMBER.sub("", line).strip() for line in lines]
    return questions[:3] if questions else [raw.strip()]


@router.callback_query(F.data == "menu_qa")
async def start_qa(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await safe_edit(callback.message, "⏳ Savollar tayyorlanmoqda...", reply_markup=None)
    raw = await generate_qa_questions(QA_TOPIC_HINT)
    questions = parse_questions(raw)
    await state.update_data(questions=questions)

    text = "❓ <b>Mumkin bo'lgan savollar:</b>\n\n" + "\n\n".join(
        f"{i+1}. {q}" for i, q in enumerate(questions)
    ) + "\n\nQaysi savolga javob berib ko'rmoqchisiz?"
    await safe_edit(callback.message, text, reply_markup=kb.qa_question_keyboard(len(questions)))


@router.callback_query(F.data.startswith("qa_pick:"))
async def pick_question(callback: CallbackQuery, state: FSMContext):
    idx = int(callback.data.split(":", 1)[1])
    data = await state.get_data()
    questions = data.get("questions", [])
    if idx >= len(questions):
        await callback.answer("Xatolik, qaytadan urinib ko'ring.", show_alert=True)
        return

    question = questions[idx]
    await state.update_data(current_question=question)
    await state.set_state(QAStates.waiting_for_answer)

    text = f"❓ <b>Savol:</b> {question}\n\nEndi javobingizni yozing yoki 🎤 ovozli xabar yuboring:"
    await safe_edit(callback.message, text, reply_markup=kb.back_to_menu())
    await callback.answer()


@router.message(QAStates.waiting_for_answer, F.voice)
async def receive_voice_answer(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    question = data.get("current_question", "")

    thinking = await message.answer("⏳ Ovoz matnga aylantirilmoqda...")

    file = await bot.get_file(message.voice.file_id)
    local_path = f"/tmp/qa_voice_{message.from_user.id}_{int(time.time())}.ogg"
    await bot.download_file(file.file_path, local_path)

    try:
        text, duration = transcribe(local_path)
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)

    if not text:
        await safe_edit(thinking, 
            "Ovozni tanimadim 😕 Aniqroq gapirib qayta yuboring, yoki matn bilan yozing.",
            reply_markup=kb.back_to_menu(),
        )
        await state.clear()
        return

    word_count = len(text.split())
    wpm = round(word_count / (duration / 60), 1) if duration > 0 else 0

    feedback = await evaluate_speaking(question, text, wpm, duration)
    await db.log_practice(message.from_user.id, "qa")

    result_text = (
        f"📝 <b>Eshitilgan matn:</b> <i>{text}</i>\n"
        f"⏱ {duration:.0f}s | {wpm} so'z/daqiqa\n\n"
        f"📋 <b>Baho:</b>\n{feedback}"
    )
    await safe_edit(thinking, result_text, reply_markup=kb.back_to_menu())
    await state.clear()


@router.message(QAStates.waiting_for_answer, F.text)
async def receive_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    question = data.get("current_question", "")

    thinking = await message.answer("⏳ Baholanmoqda...")
    feedback = await evaluate_qa_answer(question, message.text)
    await db.log_practice(message.from_user.id, "qa")

    await safe_edit(thinking, f"📋 <b>Baho:</b>\n\n{feedback}", reply_markup=kb.back_to_menu())
    await state.clear()
