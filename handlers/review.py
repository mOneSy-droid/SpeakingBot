"""Handler for spaced repetition review"""
from aiogram import Router, F
from aiogram.types import CallbackQuery

import database as db
import keyboards as kb
from content import VOCAB_WEEKS
from utils import safe_edit
import random
from datetime import datetime, timedelta, timezone

router = Router()


@router.callback_query(F.data == "menu_review")
async def show_review_menu(callback: CallbackQuery):
    """Show spaced repetition review menu"""
    telegram_id = callback.from_user.id
    
    # Get words needing review
    review_words = await db.get_words_for_review(telegram_id)
    
    if not review_words:
        text = (
            "✅ Bugun qayta o'rgatish uchun so'z yo'q!\n\n"
            "Yangi so'zlar o'rgangach, ular ko'p vaqtdan keyin qayta ko'rinadi.\n\n"
            "💡 Bu 'spaced repetition' usuli — umuman unuta olmang! 🧠"
        )
        keyboard = kb.back_to_menu()
    else:
        text = (
            f"🔁 **Spaced Repetition Review**\n\n"
            f"📚 Qayta o'rgatish uchun {len(review_words)} ta so'z bor.\n\n"
            f"Ushbu so'zlarni qayta o'rganish sizning xotirjamg'iningizni kuchaytiradi!"
        )
        
        keyboard = kb.InlineKeyboardMarkup(
            inline_keyboard=[
                [kb.InlineKeyboardButton(text=f"📖 Boshla ({len(review_words)} so'z)", callback_data="start_review")],
                [kb.InlineKeyboardButton(text="⬅️ Menyu", callback_data="menu_back")],
            ]
        )
    
    await safe_edit(callback.message, text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "start_review")
async def start_review(callback: CallbackQuery, state):
    """Start spaced repetition review session"""
    telegram_id = callback.from_user.id
    
    # Get words for review
    review_words = await db.get_words_for_review(telegram_id)
    
    if not review_words:
        await callback.answer("❌ Qayta o'rgatish uchun so'z yo'q!", show_alert=True)
        return
    
    # Save session data
    await state.update_data(
        review_words=review_words,
        current_review_index=0,
        review_results={}
    )
    
    # Show first word
    await show_next_review_word(callback, state)


async def show_next_review_word(callback: CallbackQuery, state):
    """Show next word in review session"""
    data = await state.get_data()
    
    review_words = data.get("review_words", [])
    current_index = data.get("current_review_index", 0)
    
    if current_index >= len(review_words):
        # Session complete
        await show_review_results(callback, state)
        return
    
    word_text = review_words[current_index]
    
    # Find word details from VOCAB_WEEKS
    word_data = find_word_in_vocab(word_text)
    
    if not word_data:
        current_index += 1
        await state.update_data(current_review_index=current_index)
        await show_next_review_word(callback, state)
        return
    
    progress = f"{current_index + 1}/{len(review_words)}"
    
    text = (
        f"🔁 Spaced Repetition [{progress}]\n\n"
        f"❓ Quyidagi so'zning ma'nosini eslaysizmi?\n\n"
        f"<b>{word_data['word']}</b>\n\n"
        f"Javobingizni eslashing:"
    )
    
    keyboard = kb.InlineKeyboardMarkup(
        inline_keyboard=[
            [kb.InlineKeyboardButton(text="✅ Ha, eslaydi", callback_data=f"review_correct:{current_index}")],
            [kb.InlineKeyboardButton(text="❌ Unuttim", callback_data=f"review_incorrect:{current_index}")],
            [kb.InlineKeyboardButton(text="👀 Javob ko'rish", callback_data=f"review_peek:{current_index}")],
        ]
    )
    
    await safe_edit(callback.message, text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("review_peek:"))
async def peek_answer(callback: CallbackQuery, state):
    """Show the answer to review word"""
    current_index = int(callback.data.split(":")[1])
    
    data = await state.get_data()
    review_words = data.get("review_words", [])
    word_text = review_words[current_index]
    word_data = find_word_in_vocab(word_text)
    
    if word_data:
        text = (
            f"📖 Javob:\n\n"
            f"<b>{word_data['word']}</b>\n"
            f"🇺🇿 {word_data['translation']}\n\n"
            f"💬 <i>{word_data['example']}</i>\n\n"
            f"Endi eslaysizmi?"
        )
        
        keyboard = kb.InlineKeyboardMarkup(
            inline_keyboard=[
                [kb.InlineKeyboardButton(text="✅ Ha, endi eslaydi", callback_data=f"review_correct:{current_index}")],
                [kb.InlineKeyboardButton(text="❌ Hali unuttim", callback_data=f"review_incorrect:{current_index}")],
            ]
        )
        
        await safe_edit(callback.message, text, reply_markup=keyboard)
    
    await callback.answer()


@router.callback_query(F.data.startswith("review_correct:"))
async def mark_correct(callback: CallbackQuery, state):
    """Mark review word as remembered"""
    current_index = int(callback.data.split(":")[1])
    
    data = await state.get_data()
    review_words = data.get("review_words", [])
    word_text = review_words[current_index]
    
    # Schedule next review in 7 days
    await db.set_next_review(callback.from_user.id, word_text, days=7)
    
    # Move to next
    current_index += 1
    await state.update_data(current_review_index=current_index)
    
    await callback.answer("✅ Ajoyib!", show_alert=False)
    await show_next_review_word(callback, state)


@router.callback_query(F.data.startswith("review_incorrect:"))
async def mark_incorrect(callback: CallbackQuery, state):
    """Mark review word as forgotten"""
    current_index = int(callback.data.split(":")[1])
    
    data = await state.get_data()
    review_words = data.get("review_words", [])
    word_text = review_words[current_index]
    
    # Schedule next review in 2 days
    await db.set_next_review(callback.from_user.id, word_text, days=2)
    
    # Move to next
    current_index += 1
    await state.update_data(current_review_index=current_index)
    
    await callback.answer("Xavf yo'q, qayta o'rganamiz!", show_alert=False)
    await show_next_review_word(callback, state)


async def show_review_results(callback: CallbackQuery, state):
    """Show review session results"""
    data = await state.get_data()
    review_words = data.get("review_words", [])
    
    text = (
        f"✅ Spaced Repetition sessiyasi yakunlandi!\n\n"
        f"📊 Natija:\n"
        f"• Jami so'z: {len(review_words)}\n"
        f"• Qayta o'rganildi\n\n"
        f"🧠 Xotirjamg'ingizni barqaror qilish uchun har qanday vaqtda qayta o'rgana olasiz.\n\n"
        f"Yaxshi ishladi! 🎉"
    )
    
    keyboard = kb.InlineKeyboardMarkup(
        inline_keyboard=[
            [kb.InlineKeyboardButton(text="📖 Yana boshla", callback_data="menu_review")],
            [kb.InlineKeyboardButton(text="⬅️ Menyu", callback_data="menu_back")],
        ]
    )
    
    await safe_edit(callback.message, text, reply_markup=keyboard)
    await state.clear()
    await callback.answer()


def find_word_in_vocab(word: str) -> dict | None:
    """Find word details from VOCAB_WEEKS"""
    for week_words in VOCAB_WEEKS.values():
        for word_data in week_words:
            if word_data['word'].lower() == word.lower():
                return word_data
    return None
