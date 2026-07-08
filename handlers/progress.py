from datetime import datetime, timezone
from aiogram import Router, F
from aiogram.types import CallbackQuery

import database as db
import keyboards as kb
from utils import safe_edit

router = Router()

PLAN_TEXT = (
    "📅 <b>4 haftalik reja</b>\n\n"
    "<b>1-hafta:</b> Tanishtiruv va partnership so'zlari + oddiy structure'lar\n"
    "<b>2-hafta:</b> Ta'lim tizimi so'zlari (curriculum, scholarship, admission)\n"
    "<b>3-hafta:</b> Biznes/muzokara so'zlari + Q&A mashqlarini boshlash\n"
    "<b>4-hafta:</b> To'liq speech matnini tayyorlash va tuzatish, ko'p Q&A mashqi\n\n"
    "Har kuni 10-15 daqiqa: 5 ta yangi so'z + 1 ta grammar mashq yetarli. "
    "Speech matningiz tayyor bo'lgach, uni 'Speech tuzatish' bo'limiga yuboring."
)


@router.callback_query(F.data == "menu_plan")
async def show_plan(callback: CallbackQuery):
    await safe_edit(callback.message, PLAN_TEXT, reply_markup=kb.back_to_menu())
    await callback.answer()


@router.callback_query(F.data == "menu_progress")
async def show_progress(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    stats = await db.get_progress_stats(telegram_id)
    joined_at = await db.get_joined_at(telegram_id)
    days_active = (datetime.now(timezone.utc) - joined_at.astimezone(timezone.utc)).days + 1

    text = (
        "📊 <b>Sizning progressingiz:</b>\n\n"
        f"🗓 Faol kunlar: {days_active}\n"
        f"📚 O'rganilgan so'zlar: {stats['words_learned']}\n"
        f"🗣 Grammar mashqlari: {stats['structure_practice']}\n"
        f"🎤 Speaking mashqlari: {stats['speaking_practice']}\n"
        f"✍️ Speech tekshiruvlari: {stats['speech_reviews']}\n"
        f"❓ Q&A mashqlari: {stats['qa_practice']}\n\n"
        "Davom eting, speech kuniga tayyor bo'lasiz! 💪"
    )
    await safe_edit(callback.message, text, reply_markup=kb.back_to_menu())
    await callback.answer()
