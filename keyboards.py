from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📚 Vocabulary", callback_data="menu_vocab")],
            [InlineKeyboardButton(text="📝 Translation Practice", callback_data="menu_translation_practice")],
            [InlineKeyboardButton(text="🎧 Talaffuz (TTS)", callback_data="menu_pronunciation")],
            [InlineKeyboardButton(text="🔁 Qayta o'rgatish", callback_data="menu_review")],
            [InlineKeyboardButton(text="🗣 Grammar Practice", callback_data="menu_practice")],
            [InlineKeyboardButton(text="🎤 Speaking practice", callback_data="menu_speaking")],
            [InlineKeyboardButton(text="⏱️ Timed Practice", callback_data="menu_timed_practice")],
            [InlineKeyboardButton(text="🎭 Mock Meeting", callback_data="menu_mock_meeting")],
            [InlineKeyboardButton(text="✍️ Speech tuzatish", callback_data="menu_speech")],
            [InlineKeyboardButton(text="❓ Q&A tayyorgarlik", callback_data="menu_qa")],
            [InlineKeyboardButton(text="📊 Progress", callback_data="menu_progress")],
            [InlineKeyboardButton(text="📈 Haftalik hisobot", callback_data="menu_weekly_report")],
            [InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="menu_settings")],
            [InlineKeyboardButton(text="📅 4 haftalik reja", callback_data="menu_plan")],
        ]
    )


def back_to_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⬅️ Menyu", callback_data="menu_back")]]
    )


def vocab_word_keyboard(word: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Bildim", callback_data=f"learned:{word}")],
            [InlineKeyboardButton(text="➡️ Keyingi so'z", callback_data="next_word")],
            [InlineKeyboardButton(text="⬅️ Menyu", callback_data="menu_back")],
        ]
    )


def translation_practice_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Bilmadim", callback_data="translation_missed")],
            [InlineKeyboardButton(text="⬅️ Menyu", callback_data="menu_back")],
        ]
    )


def practice_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔁 Yana bitta structure", callback_data="menu_practice")],
            [InlineKeyboardButton(text="⬅️ Menyu", callback_data="menu_back")],
        ]
    )


def qa_question_keyboard(count: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=f"Savol {i+1}", callback_data=f"qa_pick:{i}")]
        for i in range(count)
    ]
    buttons.append([InlineKeyboardButton(text="⬅️ Menyu", callback_data="menu_back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def speaking_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎤 Yana bitta savol", callback_data="menu_speaking")],
            [InlineKeyboardButton(text="⬅️ Menyu", callback_data="menu_back")],
        ]
    )
