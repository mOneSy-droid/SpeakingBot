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


TOKEN_ALIASES = {
    "hamkorlik": "hamkorlik",
    "birgalik": "hamkorlik",
    "birgalikda": "hamkorlik",
    "cooperation": "hamkorlik",
    "partnership": "hamkorlik",
    "collaboration": "hamkorlik",
    "qabul": "qabul",
    "admission": "qabul",
    "acceptance": "qabul",
    "kirish": "qabul",
    "mezon": "mezon",
    "mezonlari": "mezon",
    "criteria": "mezon",
    "requirements": "mezon",
    "requirement": "mezon",
    "shartlar": "mezon",
    "talablar": "mezon",
    "taklif": "taklif",
    "offer": "taklif",
    "proposal": "taklif",
    "teklif": "taklif",
    "stipendiya": "stipendiya",
    "scholarship": "stipendiya",
    "grant": "stipendiya",
    "delegatsiya": "delegatsiya",
    "delegation": "delegatsiya",
    "nomidan": "nomidan",
    "for": "nomidan",
    "uchun": "nomidan",
    "tomonidan": "nomidan",
    "oquv": "oquv",
    "dastur": "dastur",
    "curriculum": "dastur",
    "program": "dastur",
    "programme": "dastur",
    "reja": "dastur",
    "manfaat": "manfaat",
    "benefit": "manfaat",
    "benefits": "manfaat",
    "ozoaro": "ozoaro",
    "oztaro": "ozoaro",
}


def normalize_text(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def normalize_tokens(text: str) -> set[str]:
    normalized = normalize_text(text)
    if not normalized:
        return set()

    return {TOKEN_ALIASES.get(token, token) for token in normalized.split() if token}


def get_vocab_items() -> list[dict]:
    return [item for week_words in VOCAB_WEEKS.values() for item in week_words]


def add_missed_word(missed_words: list[dict], item: dict | None) -> list[dict]:
    if not item:
        return missed_words

    if any(existing.get("word") == item.get("word") for existing in missed_words):
        return missed_words

    return [*missed_words, {"word": item["word"], "translation": item["translation"]}]


def is_translation_correct(user_answer: str | None, expected_translation: str | None) -> bool:
    if not user_answer or not expected_translation:
        return False

    user = normalize_text(user_answer)
    expected = normalize_text(expected_translation)

    if not user or not expected:
        return False

    if user == expected:
        return True

    expected_parts = [part.strip() for part in expected.split(",") if part.strip()]
    if user in expected_parts:
        return True

    user_tokens = normalize_tokens(user_answer)
    expected_tokens = set()
    for part in expected_parts:
        expected_tokens.update(normalize_tokens(part))

    if user_tokens and expected_tokens and (user_tokens & expected_tokens):
        return True

    synonyms = {
        "hamkorlik": {"hamkorlik", "birgalik", "birgalikda ishlash", "hamkorlikda", "hamkorlik qilish"},
        "taklif": {"taklif", "offer", "proposal", "teklif"},
        "qabul": {"qabul", "acceptance", "kirish", "olish"},
        "talablarga muvofiqlik": {"talablarga muvofiqlik", "muvofiqlik", "compliance", "moslik"},
        "oquv dasturi": {"oquv dasturi", "dastur", "curriculum", "oquv rejasi"},
        "stipendiya": {"stipendiya", "scholarship", "grant"},
        "delegatsiya": {"delegatsiya", "delegation"},
        "nomidan": {"nomidan", "for", "uchun", "tomonidan"},
    }

    for key, variants in synonyms.items():
        if expected.startswith(key):
            if user in variants:
                return True

    return False


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

    expected = item["translation"]
    user_answer = message.text

    if is_translation_correct(user_answer, expected):
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

    missed_words = add_missed_word(data.get("missed_words", []), item)
    await state.update_data(missed_words=missed_words)

    await message.answer(
        f"❌ Noto'g'ri. To'g'ri javob: <b>{item['translation']}</b>\n\n"
        f"Bu so'z sizning 'missed words' ro'yxatingizga qo'shildi ({len(missed_words)} ta)."
    )
