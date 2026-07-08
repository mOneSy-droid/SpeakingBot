"""Text-to-Speech service using gtts"""
import os
import asyncio
from gtts import gTTS
from pathlib import Path


AUDIO_DIR = Path("audio_files")
AUDIO_DIR.mkdir(exist_ok=True)


async def generate_speech(text: str, lang: str = "en", user_id: int = 0, word: str = "") -> str:
    """
    Generate audio file for given text using gTTS
    
    Args:
        text: Text to speak
        lang: Language code ('en' for English, 'uz' for Uzbek)
        user_id: Telegram user ID (for organizing files)
        word: Word identifier for filename
    
    Returns:
        Path to generated audio file
    """
    try:
        # Create filename
        safe_word = word.replace(" ", "_").replace("(", "").replace(")", "")[:20]
        filename = f"audio_{user_id}_{safe_word}.mp3" if word else f"audio_{user_id}.mp3"
        filepath = AUDIO_DIR / filename
        
        # Generate audio in async-friendly way
        tts = gTTS(text, lang=lang, slow=False)
        
        # Save in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: tts.save(str(filepath)))
        
        return str(filepath)
    except Exception as e:
        print(f"Error generating speech: {e}")
        return ""


async def cleanup_old_audio(user_id: int, keep_count: int = 5):
    """Clean up old audio files for a user, keeping only recent ones"""
    try:
        user_files = sorted(
            AUDIO_DIR.glob(f"audio_{user_id}_*.mp3"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        for old_file in user_files[keep_count:]:
            old_file.unlink()
    except Exception as e:
        print(f"Error cleaning up audio: {e}")
