import random
from datetime import datetime, timezone
from aiogram import Router, F
from aiogram.types import CallbackQuery

import database as db
import keyboards as kb
from content import VOCAB_WEEKS
from utils import safe_edit

router = Router()


def current_week(joined_at: datetime) -> int:
    days = (datetime.now(timezone.utc) - joined_at.astimezone(timezone.utc)).days
    week = (days // 7) + 1
    return min(max(week, 1), 4)


async def send_word(callback: CallbackQuery, telegram_id: int):
    joined_at = await db.get_joined_at(telegram_id)
    week = current_week(joined_at)
    learned = await db.get_learned_words(telegram_id)

    week_words = VOCAB_WEEKS[week]
    remaining = [w for w in week_words if w["word"] not in learned]

    if not remaining:
        text = (
            f"🎉 {week}-haftaning barcha so'zlarini o'rgandingiz!\n\n"
            "Keyingi hafta yangi so'zlar ochiladi, yoki /start orqali menyuga qayting."
        )
        await safe_edit(callback.message, text, reply_markup=kb.back_to_menu())
        return

    item = random.choice(remaining)
    text = (
        f"📚 {week}-hafta so'zi:\n\n"
        f"🔤 <b>{item['word']}</b>\n"
        f"🇺🇿 {item['translation']}\n\n"
        f"💬 <i>{item['example']}</i>"
    )
    await safe_edit(callback.message, text, reply_markup=kb.vocab_word_keyboard(item["word"]))


@router.callback_query(F.data == "menu_vocab")
async def show_vocab(callback: CallbackQuery):
    await send_word(callback, callback.from_user.id)
    await callback.answer()


@router.callback_query(F.data == "next_word")
async def next_word(callback: CallbackQuery):
    await send_word(callback, callback.from_user.id)
    await callback.answer()


@router.callback_query(F.data.startswith("learned:"))
async def mark_learned(callback: CallbackQuery):
    word = callback.data.split(":", 1)[1]
    await db.mark_word_learned(callback.from_user.id, word)
    await callback.answer("Ajoyib! ✅")
    await send_word(callback, callback.from_user.id)
