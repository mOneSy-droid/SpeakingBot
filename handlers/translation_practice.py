import random
import re

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import keyboards as kb
from content import VOCAB_WEEKS
from states import TranslationPracticeStates
from utils import safe_edit

router = Router()


def normalize_text(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def get_vocab_items() -> list[dict]:
    return [item for week_words in VOCAB_WEEKS.values() for item in week_words]


async def show_translation_question(callback: CallbackQuery, state: FSMContext):
    items = get_vocab_items()
    if not items:
        await safe_edit(callback.message, "No vocabulary items available yet.", reply_markup=kb.back_to_menu())
        return

    item = random.choice(items)
    await state.set_state(TranslationPracticeStates.waiting_for_translation)
    await state.update_data(current_word=item)

    text = (
        "📝 <b>Translation practice</b>\n\n"
        f"English word: <b>{item['word']}</b>\n\n"
        "Uning o'zbekcha tarjimasini yozing.\n"
        "Agar noto'g'ri yozsangiz, men to'g'ri javobni ko'rsataman va siz yana urinib ko'rasiz."
    )
    await safe_edit(callback.message, text, reply_markup=kb.back_to_menu())
    await callback.answer()


@router.callback_query(F.data == "menu_translation_practice")
async def start_translation_practice(callback: CallbackQuery, state: FSMContext):
    await show_translation_question(callback, state)


@router.message(TranslationPracticeStates.waiting_for_translation)
async def receive_translation(message: Message, state: FSMContext):
    data = await state.get_data()
    item = data.get("current_word")
    if not item:
        await message.answer("Iltimos, yangi mashqni boshlang.")
        return

    expected = normalize_text(item["translation"])
    user_answer = normalize_text(message.text)

    if user_answer == expected:
        await message.answer(
            f"✅ To'g'ri! <b>{item['word']}</b> -> <b>{item['translation']}</b>",
            reply_markup=kb.InlineKeyboardMarkup(
                inline_keyboard=[
                    [kb.InlineKeyboardButton(text="➡️ Keyingi so'z", callback_data="menu_translation_practice")],
                    [kb.InlineKeyboardButton(text="⬅️ Menyu", callback_data="menu_back")],
                ]
            ),
        )
        await state.clear()
        return

    await message.answer(
        f"❌ Noto'g'ri. To'g'ri javob: <b>{item['translation']}</b>\n\n"
        "Yana urinib ko'ring — men sizni shu so'z bilan davom ettiraman."
    )
