"""Handler for weekly reports and voice history"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from datetime import datetime, timezone, timedelta

import database as db
import keyboards as kb
from export_service import create_report_pdf, export_voice_history_pdf
from utils import safe_edit

router = Router()


@router.callback_query(F.data == "menu_weekly_report")
async def show_weekly_report(callback: CallbackQuery):
    """Show weekly report"""
    telegram_id = callback.from_user.id
    
    # Get stats for this week
    stats = await get_weekly_stats(telegram_id)
    
    text = (
        "📈 **Haftalik Hisobot**\n\n"
        f"📊 Statistika:\n"
        f"• Jami sessiyalar: {stats['total_sessions']}\n"
        f"• O'rgangan so'zlar: {stats['words_learned']}\n"
        f"• Progress: {stats['improvement_score']:.1f}%\n\n"
    )
    
    # Get practice breakdown
    cursor_data = await db.get_progress_stats(telegram_id)
    text += "🎯 Faoliyat turlari:\n"
    text += f"• Vocabulary: {cursor_data.get('structure_practice', 0)}\n"
    text += f"• Grammar: {cursor_data.get('qa_practice', 0)}\n"
    text += f"• Speaking: {cursor_data.get('speaking_practice', 0)}\n"
    text += f"• Speech Review: {cursor_data.get('speech_reviews', 0)}\n\n"
    
    if stats['total_sessions'] > 0:
        text += "✨ Yaxshi ishladi bu hafta!\n"
    else:
        text += "💡 Bu haftada hali mashq qilmadingiz.\n"
    
    keyboard = kb.InlineKeyboardMarkup(
        inline_keyboard=[
            [kb.InlineKeyboardButton(text="📄 PDF sifatida yuborish", callback_data="export_report_pdf")],
            [kb.InlineKeyboardButton(text="🎤 Ovozli mashqlar tarixi", callback_data="menu_voice_history")],
            [kb.InlineKeyboardButton(text="⬅️ Menyu", callback_data="menu_back")],
        ]
    )
    
    await safe_edit(callback.message, text, reply_markup=keyboard)
    await callback.answer()


async def get_weekly_stats(telegram_id: int) -> dict:
    """Calculate weekly statistics"""
    from datetime import datetime, timezone, timedelta
    
    now = datetime.now(timezone.utc)
    week_start = (now - timedelta(days=now.weekday())).isoformat()
    
    # Get practice log for this week
    async with __import__('aiosqlite').connect(__import__('config').DB_PATH) as db_conn:
        cursor = await db_conn.execute(
            "SELECT COUNT(*) FROM practice_log WHERE telegram_id = ? AND created_at >= ?",
            (telegram_id, week_start),
        )
        sessions = (await cursor.fetchone())[0]
        
        # Get words learned this week
        cursor = await db_conn.execute(
            "SELECT COUNT(*) FROM learned_words WHERE telegram_id = ? AND learned_at >= ?",
            (telegram_id, week_start),
        )
        words = (await cursor.fetchone())[0]
    
    # Calculate improvement
    total_sessions = await _get_total_sessions(telegram_id)
    improvement = (sessions / max(total_sessions or 1, 1)) * 100 if total_sessions else 0
    
    return {
        "total_sessions": sessions,
        "words_learned": words,
        "improvement_score": improvement,
    }


async def _get_total_sessions(telegram_id: int) -> int:
    """Get total practice sessions for comparison"""
    async with __import__('aiosqlite').connect(__import__('config').DB_PATH) as db_conn:
        cursor = await db_conn.execute(
            "SELECT COUNT(*) FROM practice_log WHERE telegram_id = ?",
            (telegram_id,),
        )
        return (await cursor.fetchone())[0]


@router.callback_query(F.data == "export_report_pdf")
async def export_report_pdf(callback: CallbackQuery):
    """Export weekly report as PDF"""
    telegram_id = callback.from_user.id
    
    thinking = await callback.message.answer("⏳ PDF tayyorlanmoqda...")
    
    try:
        stats = await get_weekly_stats(telegram_id)
        recordings = await db.get_voice_recordings(telegram_id, limit=5)
        
        # Create report
        from handlers.vocab import current_week
        joined_at = await db.get_joined_at(telegram_id)
        week = current_week(joined_at)
        
        pdf_path = create_report_pdf(
            telegram_id,
            week,
            stats,
            recordings,
        )
        
        if pdf_path:
            # Send PDF
            with open(pdf_path, 'rb') as pdf_file:
                await callback.message.answer_document(
                    pdf_file,
                    caption="📄 Sizning haftalik hisobotingiz"
                )
            
            await thinking.delete()
        else:
            await safe_edit(thinking, "❌ PDF yaratishda xato", reply_markup=kb.back_to_menu())
    except Exception as e:
        print(f"Error: {e}")
        await safe_edit(thinking, "❌ Xatolik yuz berdi", reply_markup=kb.back_to_menu())


@router.callback_query(F.data == "menu_voice_history")
async def show_voice_history(callback: CallbackQuery):
    """Show voice recording history"""
    telegram_id = callback.from_user.id
    
    recordings = await db.get_voice_recordings(telegram_id, limit=10)
    
    if not recordings:
        text = "🎤 Ovozli mashqlar tarixi bo'sh.\n\nSpeaking practise'da ovozli javoblar yuboring!"
        keyboard = kb.InlineKeyboardMarkup(
            inline_keyboard=[
                [kb.InlineKeyboardButton(text="🎤 Speaking Practice", callback_data="menu_speaking")],
                [kb.InlineKeyboardButton(text="⬅️ Menyu", callback_data="menu_back")],
            ]
        )
    else:
        text = "🎤 **Ovozli Mashqlar Tarixi**\n\n"
        text += f"📊 Jami: {len(recordings)} ta mashq\n\n"
        text += "Eng so'nggi 5 ta:\n\n"
        
        for i, rec in enumerate(recordings[:5], 1):
            date = rec.get('recorded_at', '')[:10]
            wpm = rec.get('wpm', 0)
            fillers = rec.get('filler_count', 0)
            score = rec.get('quality_score', 0)
            
            text += f"{i}. {date}\n"
            text += f"   ⏱ {wpm} WPM | 🗣 {fillers} filler | ⭐ {score}%\n\n"
        
        keyboard = kb.InlineKeyboardMarkup(
            inline_keyboard=[
                [kb.InlineKeyboardButton(text="📄 PDF sifatida eksport", callback_data="export_voice_history_pdf")],
                [kb.InlineKeyboardButton(text="📊 Tafsilotlar", callback_data="voice_history_details")],
                [kb.InlineKeyboardButton(text="⬅️ Menyu", callback_data="menu_back")],
            ]
        )
    
    await safe_edit(callback.message, text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "export_voice_history_pdf")
async def export_voice_history_pdf(callback: CallbackQuery):
    """Export voice history as PDF"""
    telegram_id = callback.from_user.id
    
    thinking = await callback.message.answer("⏳ PDF tayyorlanmoqda...")
    
    try:
        recordings = await db.get_voice_recordings(telegram_id, limit=20)
        
        if not recordings:
            await safe_edit(thinking, "❌ Eksport qilish uchun ovozli mashqlar yo'q", reply_markup=kb.back_to_menu())
            return
        
        pdf_path = export_voice_history_pdf(telegram_id, recordings)
        
        if pdf_path:
            with open(pdf_path, 'rb') as pdf_file:
                await callback.message.answer_document(
                    pdf_file,
                    caption="🎤 Sizning ovozli mashqlar tarixi"
                )
            await thinking.delete()
        else:
            await safe_edit(thinking, "❌ PDF yaratishda xato", reply_markup=kb.back_to_menu())
    except Exception as e:
        print(f"Error: {e}")
        await safe_edit(thinking, "❌ Xatolik yuz berdi", reply_markup=kb.back_to_menu())


@router.callback_query(F.data == "voice_history_details")
async def show_voice_history_details(callback: CallbackQuery):
    """Show detailed voice history statistics"""
    telegram_id = callback.from_user.id
    
    recordings = await db.get_voice_recordings(telegram_id, limit=20)
    
    if not recordings:
        await callback.answer("Tarixi yo'q", show_alert=True)
        return
    
    # Calculate statistics
    avg_wpm = sum(r.get('wpm', 0) for r in recordings) / len(recordings)
    total_fillers = sum(r.get('filler_count', 0) for r in recordings)
    avg_quality = sum(r.get('quality_score', 0) for r in recordings) / len(recordings)
    
    # Find improvement
    if len(recordings) >= 2:
        first_score = recordings[-1].get('quality_score', 0)
        last_score = recordings[0].get('quality_score', 0)
        improvement = last_score - first_score
    else:
        improvement = 0
    
    text = (
        "📊 **Ovozli Mashqlar Statistikasi**\n\n"
        f"📈 Jami: {len(recordings)} ta\n"
        f"⏱ O'rtacha WPM: {avg_wpm:.1f}\n"
        f"🗣 Jami filler so'zlar: {total_fillers}\n"
        f"⭐ O'rtacha sifat: {avg_quality:.1f}%\n\n"
    )
    
    if improvement > 0:
        text += f"✨ Yaxshi! {improvement:.0f}% taraqqiy qildingiz!"
    elif improvement < 0:
        text += f"⚠️ Kema keyingi sessiyalar uchun!"
    
    keyboard = kb.back_to_menu()
    await safe_edit(callback.message, text, reply_markup=keyboard)
    await callback.answer()
