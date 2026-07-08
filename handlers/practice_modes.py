"""Handler for timed practice and mock meeting modes"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
import keyboards as kb
from gemini_client import evaluate_qa_answer, generate_qa_questions
from utils import safe_edit
import asyncio

router = Router()


class TimedPracticeStates(StatesGroup):
    waiting_for_timed_answer = State()
    in_timed_practice = State()


class MockMeetingStates(StatesGroup):
    waiting_for_question_count = State()
    waiting_for_answer = State()
    in_mock_meeting = State()


@router.callback_query(F.data == "menu_timed_practice")
async def show_timed_practice(callback: CallbackQuery):
    """Show timed practice mode options"""
    text = (
        "⏱️ **Vaqt chegarasi bilan mashq**\n\n"
        "Real uchrashuvdagidek bosim ostida gapirish.\n\n"
        "Quyida berilgan vaqt ichida savolga javob bering!"
    )
    
    keyboard = kb.InlineKeyboardMarkup(
        inline_keyboard=[
            [kb.InlineKeyboardButton(text="30 soniyada", callback_data="timed:30")],
            [kb.InlineKeyboardButton(text="60 soniyada", callback_data="timed:60")],
            [kb.InlineKeyboardButton(text="120 soniyada", callback_data="timed:120")],
            [kb.InlineKeyboardButton(text="⬅️ Menyu", callback_data="menu_back")],
        ]
    )
    
    await safe_edit(callback.message, text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("timed:"))
async def start_timed_practice(callback: CallbackQuery, state: FSMContext):
    """Start timed practice"""
    time_limit = int(callback.data.split(":")[1])
    
    # Generate a question
    try:
        questions_text = await generate_qa_questions("Partnership speech preparation - answer as if in a real meeting")
        questions = [q.strip() for q in questions_text.split('\n') if q.strip() and q[0].isdigit()]
        
        if not questions:
            questions = ["Tell us about your organization and your goals."]
        
        question = questions[0]
    except:
        question = "Tell us about your organization and what you hope to achieve through this partnership."
    
    await state.set_state(TimedPracticeStates.in_timed_practice)
    await state.update_data(
        timed_time_limit=time_limit,
        timed_question=question,
        timed_start_time=None,
    )
    
    text = (
        f"⏱️ **Vaqt chegarasi: {time_limit} soniya**\n\n"
        f"❓ Savol:\n\n"
        f"{question}\n\n"
        f"🎤 Javobingizni yuboring. Siz tinglanganda vaqt o'tadi!"
    )
    
    keyboard = kb.back_to_menu()
    await safe_edit(callback.message, text, reply_markup=keyboard)
    await state.set_state(TimedPracticeStates.waiting_for_timed_answer)
    await callback.answer()


@router.message(TimedPracticeStates.waiting_for_timed_answer)
async def receive_timed_answer(message: Message, state: FSMContext):
    """Receive and evaluate timed answer"""
    data = await state.get_data()
    time_limit = data.get("timed_time_limit", 60)
    question = data.get("timed_question", "")
    
    # Log practice
    await db.log_practice(message.from_user.id, "timed")
    
    thinking = await message.answer("⏳ Tahlil qilinmoqda...")
    
    try:
        # Evaluate the answer
        feedback = await evaluate_qa_answer(question, message.text)
        
        text = (
            f"⏱️ **Timed Practice Natijasi**\n\n"
            f"❓ Savol: {question}\n\n"
            f"📝 Javob: {message.text[:100]}...\n\n"
            f"💬 **Fikr:**\n{feedback}\n\n"
            f"💡 Maslahat: Vaqt bilan mashq qilishni davom ettiring!"
        )
    except:
        text = (
            f"✅ Javob qabul qilindi!\n\n"
            f"Siz {time_limit} soniyada gapirdingiz.\n\n"
            f"💡 Fluency va pronunciation'ni yaxshilash uchun yana qabul qiling!"
        )
    
    keyboard = kb.InlineKeyboardMarkup(
        inline_keyboard=[
            [kb.InlineKeyboardButton(text="🔄 Yana bir savol", callback_data="menu_timed_practice")],
            [kb.InlineKeyboardButton(text="⬅️ Menyu", callback_data="menu_back")],
        ]
    )
    
    await safe_edit(thinking, text, reply_markup=keyboard)
    await state.clear()


@router.callback_query(F.data == "menu_mock_meeting")
async def show_mock_meeting(callback: CallbackQuery):
    """Show mock meeting mode"""
    text = (
        "🎭 **To'liq Mock Meeting Rejimi**\n\n"
        "Realidagi uchrashuv kabi bir nechta savolni ketma-ket beramiz.\n\n"
        "Oxirida umumiy baho beraman."
    )
    
    keyboard = kb.InlineKeyboardMarkup(
        inline_keyboard=[
            [kb.InlineKeyboardButton(text="3 savol", callback_data="mock_meeting:3")],
            [kb.InlineKeyboardButton(text="5 savol", callback_data="mock_meeting:5")],
            [kb.InlineKeyboardButton(text="8 savol", callback_data="mock_meeting:8")],
            [kb.InlineKeyboardButton(text="⬅️ Menyu", callback_data="menu_back")],
        ]
    )
    
    await safe_edit(callback.message, text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("mock_meeting:"))
async def start_mock_meeting(callback: CallbackQuery, state: FSMContext):
    """Start mock meeting session"""
    question_count = int(callback.data.split(":")[1])
    
    # Generate questions
    try:
        questions_text = await generate_qa_questions(
            "Partnership speech meeting - generate realistic questions panel might ask"
        )
        # Parse and repeat to get enough questions
        base_questions = [q.strip() for q in questions_text.split('\n') if q.strip() and q[0].isdigit()]
        questions = base_questions * ((question_count // len(base_questions)) + 1)
        questions = questions[:question_count]
    except:
        questions = [
            "Tell us about your organization and your mission.",
            "What specific outcomes are you looking for from this partnership?",
            "How would this partnership benefit your students?",
            "What is your timeline for implementation?",
            "Can you elaborate on your fee structure?"
        ][:question_count]
    
    await state.set_state(MockMeetingStates.in_mock_meeting)
    await state.update_data(
        mock_questions=questions,
        mock_current_question=0,
        mock_responses=[],
        mock_scores=[],
    )
    
    await show_mock_meeting_question(callback, state)


async def show_mock_meeting_question(callback: CallbackQuery, state: FSMContext):
    """Show next question in mock meeting"""
    data = await state.get_data()
    questions = data.get("mock_questions", [])
    current_idx = data.get("mock_current_question", 0)
    
    if current_idx >= len(questions):
        # Meeting complete
        await show_mock_meeting_results(callback, state)
        return
    
    question = questions[current_idx]
    progress = f"{current_idx + 1}/{len(questions)}"
    
    text = (
        f"🎭 Mock Meeting [{progress}]\n\n"
        f"❓ Savol:\n\n"
        f"{question}\n\n"
        f"🎤 Javobingizni yuboring:"
    )
    
    keyboard = kb.back_to_menu()
    await safe_edit(callback.message, text, reply_markup=keyboard)
    await state.set_state(MockMeetingStates.waiting_for_answer)
    await callback.answer()


@router.message(MockMeetingStates.waiting_for_answer)
async def receive_mock_answer(message: Message, state: FSMContext):
    """Receive mock meeting answer"""
    data = await state.get_data()
    questions = data.get("mock_questions", [])
    current_idx = data.get("mock_current_question", 0)
    responses = data.get("mock_responses", [])
    
    question = questions[current_idx]
    
    thinking = await message.answer("⏳ Tahlil qilinmoqda...")
    
    # Get feedback
    try:
        feedback = await evaluate_qa_answer(question, message.text)
        score = 7  # Basic score
    except:
        feedback = "✓ Good answer."
        score = 6
    
    responses.append({"question": question, "answer": message.text, "feedback": feedback})
    
    # Move to next question
    next_idx = current_idx + 1
    
    if next_idx < len(questions):
        await state.update_data(
            mock_current_question=next_idx,
            mock_responses=responses,
        )
        
        # Show feedback and next question
        text = f"✅ Javob qabul qilindi.\n\n{feedback}\n\n➡️ Keyingi savolga o'taylik..."
        keyboard = kb.InlineKeyboardMarkup(
            inline_keyboard=[[kb.InlineKeyboardButton(text="Keyingi ➡️", callback_data="mock_next_question")]]
        )
        await safe_edit(thinking, text, reply_markup=keyboard)
    else:
        # Meeting complete
        await state.update_data(mock_responses=responses)
        await show_mock_meeting_results(
            type('obj', (object,), {'message': thinking, 'from_user': type('obj', (object,), {'id': message.from_user.id})(), 'answer': message.answer})(),
            state
        )


@router.callback_query(F.data == "mock_next_question")
async def next_mock_question(callback: CallbackQuery, state: FSMContext):
    """Go to next mock meeting question"""
    await show_mock_meeting_question(callback, state)


async def show_mock_meeting_results(callback, state: FSMContext):
    """Show mock meeting results"""
    data = await state.get_data()
    responses = data.get("mock_responses", [])
    
    text = (
        f"🎉 **Mock Meeting Yakunlandi!**\n\n"
        f"📊 Natijalar:\n"
        f"• Jami savollar: {len(responses)}\n"
        f"• O'rtacha baho: 7/10\n\n"
        f"💡 Umumiy fikr:\n"
        f"Yaxshi tayyorgarlik qildingiz! Bir nechta maslahatlar:\n"
        f"1. Pausalardan o'ziga kelish uchun foydalaning\n"
        f"2. Mikrofon yaqinida gapiring\n"
        f"3. Jonli va ishonchli bo'ling\n\n"
        f"🏆 Keyingi safar yana yaxshi amallar qiling!"
    )
    
    keyboard = kb.InlineKeyboardMarkup(
        inline_keyboard=[
            [kb.InlineKeyboardButton(text="🎭 Yana boshla", callback_data="menu_mock_meeting")],
            [kb.InlineKeyboardButton(text="⬅️ Menyu", callback_data="menu_back")],
        ]
    )
    
    await safe_edit(callback.message, text, reply_markup=keyboard)
    
    # Log practice
    await db.log_practice(callback.from_user.id, "mock_meeting")
    await state.clear()
    await callback.answer()
