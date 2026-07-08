"""Handler for user settings"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
import keyboards as kb
from reminder_scheduler import set_reminder_time, get_reminder_help
from utils import safe_edit
from filler_analyzer import get_filler_tips

router = Router()


class SettingsStates(StatesGroup):
    setting_reminder = State()


@router.callback_query(F.data == "menu_settings")
async def show_settings(callback: CallbackQuery):
    """Show settings menu"""
    telegram_id = callback.from_user.id
    
    # Get current settings
    reminder_time = await db.get_reminder_time(telegram_id)
    
    text = (
        "⚙️ **Sozlamalar**\n\n"
        f"⏰ Kunlik eslatma vaqti: {reminder_time}\n\n"
        "Quyidagini o'zgartira olasiz:"
    )
    
    keyboard = kb.InlineKeyboardMarkup(
        inline_keyboard=[
            [kb.InlineKeyboardButton(text="⏰ Eslatma vaqtini o'zgartirish", callback_data="settings_reminder")],
            [kb.InlineKeyboardButton(text="🗣 Filler so'zlarni qanday kamaytirim?", callback_data="settings_filler_tips")],
            [kb.InlineKeyboardButton(text="❓ Qo'llanma", callback_data="settings_help")],
            [kb.InlineKeyboardButton(text="⬅️ Menyu", callback_data="menu_back")],
        ]
    )
    
    await safe_edit(callback.message, text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "settings_reminder")
async def settings_reminder(callback: CallbackQuery, state: FSMContext):
    """Setting reminder time"""
    await state.set_state(SettingsStates.setting_reminder)
    
    text = (
        "⏰ **Eslatma vaqtini kiriting**\n\n"
        "Formatda: HH:MM (masalan: 08:00, 14:30)\n\n"
        "Kiritilgan vaqtda kunlik xabar olasiz."
    )
    
    keyboard = kb.back_to_menu()
    await safe_edit(callback.message, text, reply_markup=keyboard)
    await callback.answer()


@router.message(SettingsStates.setting_reminder)
async def receive_reminder_time(message: Message, state: FSMContext):
    """Receive reminder time from user"""
    time_str = message.text.strip()
    
    # Validate and set
    if await set_reminder_time(message.from_user.id, time_str):
        text = f"✅ Eslatma vaqti {time_str} ga o'zgartirildi!\n\n"
        text += f"Siz har kuni {time_str} da xabar olasiz."
        
        keyboard = kb.InlineKeyboardMarkup(
            inline_keyboard=[
                [kb.InlineKeyboardButton(text="⚙️ Boshqa sozlamalar", callback_data="menu_settings")],
                [kb.InlineKeyboardButton(text="⬅️ Menyu", callback_data="menu_back")],
            ]
        )
        
        await message.answer(text, reply_markup=keyboard)
    else:
        text = "❌ Noto'g'ri vaqt formati!\n\n"
        text += "Iltimos, HH:MM formatida kiriting (masalan: 08:00)"
        
        keyboard = kb.back_to_menu()
        await message.answer(text, reply_markup=keyboard)
    
    await state.clear()


@router.callback_query(F.data == "settings_filler_tips")
async def settings_filler_tips(callback: CallbackQuery):
    """Show filler word reduction tips"""
    text = get_filler_tips()
    
    keyboard = kb.InlineKeyboardMarkup(
        inline_keyboard=[
            [kb.InlineKeyboardButton(text="🎤 Speaking Practice", callback_data="menu_speaking")],
            [kb.InlineKeyboardButton(text="⬅️ Sozlamalar", callback_data="menu_settings")],
        ]
    )
    
    await safe_edit(callback.message, text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "settings_help")
async def settings_help(callback: CallbackQuery):
    """Show general help"""
    text = (
        "❓ **Qo'llanma**\n\n"
        "**Mavjud xususiyatlar:**\n\n"
        "📚 **Vocabulary** — Haftali so'zlar o'rganing\n"
        "🎧 **Talaffuz** — TTS bilan so'zlarni tinglang\n"
        "🔁 **Spaced Repetition** — Unutan so'zlarni qayta o'rganing\n"
        "✍️ **Grammar Practice** — Sentence patterns amaliyoti\n"
        "🎤 **Speaking Practice** — Ovozli javoblar\n"
        "⏱️ **Timed Practice** — Vaqt chegarasi bilan\n"
        "🎭 **Mock Meeting** — Real meeting simulyatsiyasi\n"
        "✍️ **Speech Review** — Nutqni tuzatish\n"
        "❓ **Q&A** — Savollar uchun tayyorgarlik\n"
        "📊 **Progress** — Umumiy statistika\n"
        "📈 **Weekly Report** — Haftalik xulosa\n\n"
        "💡 **Maslahat:** Har kuni kamida 30 minut mashq qiling!"
    )
    
    keyboard = kb.InlineKeyboardMarkup(
        inline_keyboard=[
            [kb.InlineKeyboardButton(text="⬅️ Sozlamalar", callback_data="menu_settings")],
        ]
    )
    
    await safe_edit(callback.message, text, reply_markup=keyboard)
    await callback.answer()
