"""Handler for TTS pronunciation samples for vocabulary"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

import database as db
import keyboards as kb
from content import VOCAB_WEEKS
from tts_service import generate_speech
from utils import safe_edit
from handlers.vocab import current_week
import random

router = Router()


@router.callback_query(F.data == "menu_pronunciation")
async def show_pronunciation_menu(callback: CallbackQuery):
    """Show pronunciation practice menu"""
    text = (
        "🎧 **Talaffuz namunasi**\n\n"
        "Bot sizga so'zlarni ovoz chiqarib aytib beradi, siz takrorlaysiz.\n\n"
        "Quyidagi variantlardan tanlang:"
    )
    keyboard = kb.InlineKeyboardMarkup(
        inline_keyboard=[
            [kb.InlineKeyboardButton(text="📚 Hozirgi hafta so'zlari", callback_data="tts_current_week")],
            [kb.InlineKeyboardButton(text="🔄 Oldingi haftalar", callback_data="tts_prev_weeks")],
            [kb.InlineKeyboardButton(text="⬅️ Menyu", callback_data="menu_back")],
        ]
    )
    await safe_edit(callback.message, text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "tts_current_week")
async def tts_current_week(callback: CallbackQuery, state: FSMContext):
    """TTS for current week's vocabulary"""
    joined_at = await db.get_joined_at(callback.from_user.id)
    week = current_week(joined_at)
    
    week_words = VOCAB_WEEKS[week]
    selected_word = random.choice(week_words)
    
    await state.update_data(tts_word=selected_word, tts_week=week)
    
    text = f"🎧 Week {week} so'zi: **{selected_word['word']}**\n\n"
    text += f"🇺🇿 Ma'nosi: {selected_word['translation']}\n\n"
    text += "⏳ Ovoz fayli tayyorlanmoqda..."
    
    msg = await safe_edit(callback.message, text, reply_markup=kb.back_to_menu())
    await callback.answer()
    
    # Generate audio
    audio_path = await generate_speech(
        selected_word['word'],
        lang='en',
        user_id=callback.from_user.id,
        word=selected_word['word']
    )
    
    if audio_path:
        # Send audio
        try:
            with open(audio_path, 'rb') as audio_file:
                await callback.message.answer_audio(
                    audio_file,
                    title=f"Pronunciation: {selected_word['word']}",
                    performer="English Speech Bot"
                )
        except Exception as e:
            print(f"Error sending audio: {e}")
            await callback.message.answer("❌ Ovoz yuborishda xato. Keyinroq qayta urinib ko'ring.")
        
        # Show next options
        text = f"🎧 Tinglandi: **{selected_word['word']}**\n\n"
        text += f"🇬🇧 {selected_word['example']}\n\n"
        text += "Endi siz ham takrorlang! 🎤"
        
        keyboard = kb.InlineKeyboardMarkup(
            inline_keyboard=[
                [kb.InlineKeyboardButton(text="🔊 Yana ayt", callback_data="tts_current_week")],
                [kb.InlineKeyboardButton(text="➡️ Keyingi so'z", callback_data="tts_current_week")],
                [kb.InlineKeyboardButton(text="⬅️ Menyu", callback_data="menu_back")],
            ]
        )
        await safe_edit(msg, text, reply_markup=keyboard)


@router.callback_query(F.data == "tts_prev_weeks")
async def tts_prev_weeks_select(callback: CallbackQuery):
    """Select previous week for TTS practice"""
    joined_at = await db.get_joined_at(callback.from_user.id)
    current_week_num = current_week(joined_at)
    
    text = "🔄 Qaysi haftaning so'zlarini qayta tinglashni xohlaysiz?\n\n"
    
    buttons = []
    for week in range(1, current_week_num):
        buttons.append(
            [kb.InlineKeyboardButton(text=f"Week {week}", callback_data=f"tts_week:{week}")]
        )
    buttons.append([kb.InlineKeyboardButton(text="⬅️ Orqaga", callback_data="menu_pronunciation")])
    
    keyboard = kb.InlineKeyboardMarkup(inline_keyboard=buttons)
    await safe_edit(callback.message, text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("tts_week:"))
async def tts_selected_week(callback: CallbackQuery, state: FSMContext):
    """Play pronunciation for selected week"""
    week = int(callback.data.split(":")[1])
    
    if week not in VOCAB_WEEKS:
        await callback.answer("❌ Bunday hafta yo'q.", show_alert=True)
        return
    
    week_words = VOCAB_WEEKS[week]
    selected_word = random.choice(week_words)
    
    await state.update_data(tts_word=selected_word, tts_week=week)
    
    text = f"🎧 Week {week} so'zi: **{selected_word['word']}**\n\n"
    text += f"🇺🇿 Ma'nosi: {selected_word['translation']}\n\n"
    text += "⏳ Ovoz fayli tayyorlanmoqda..."
    
    msg = await safe_edit(callback.message, text, reply_markup=kb.back_to_menu())
    await callback.answer()
    
    # Generate and send audio
    audio_path = await generate_speech(
        selected_word['word'],
        lang='en',
        user_id=callback.from_user.id,
        word=selected_word['word']
    )
    
    if audio_path:
        try:
            with open(audio_path, 'rb') as audio_file:
                await callback.message.answer_audio(
                    audio_file,
                    title=f"Pronunciation: {selected_word['word']}",
                    performer="English Speech Bot"
                )
        except Exception as e:
            print(f"Error sending audio: {e}")
        
        # Show example and next options
        text = f"🎧 Tinglandi: **{selected_word['word']}**\n\n"
        text += f"🇬🇧 {selected_word['example']}\n\n"
        text += "Takrorlang! 🎤"
        
        keyboard = kb.InlineKeyboardMarkup(
            inline_keyboard=[
                [kb.InlineKeyboardButton(text="🔊 Yana ayt", callback_data=f"tts_week:{week}")],
                [kb.InlineKeyboardButton(text="➡️ Keyingi so'z", callback_data=f"tts_week:{week}")],
                [kb.InlineKeyboardButton(text="⬅️ Menyu", callback_data="menu_back")],
            ]
        )
        await safe_edit(msg, text, reply_markup=keyboard)
