from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup


async def safe_edit(message, text: str, reply_markup: InlineKeyboardMarkup | None = None):
    """edit_text wrapper that silently ignores Telegram's harmless
    'message is not modified' error (happens when the new text/markup
    is identical to what's already shown)."""
    try:
        await message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
