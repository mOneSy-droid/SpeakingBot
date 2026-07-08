from google import genai
from google.genai import types
from config import GEMINI_API_KEY, GEMINI_MODEL

client = genai.Client(api_key=GEMINI_API_KEY)


async def _ask(system: str, user_message: str, max_tokens: int = 700) -> str:
    response = await client.aio.models.generate_content(
        model=GEMINI_MODEL,
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=system,
            max_output_tokens=max_tokens,
        ),
    )
    return (response.text or "").strip()


async def check_structure_sentence(pattern: str, user_sentence: str) -> str:
    system = (
        "You are a friendly, encouraging English speaking coach helping a Central Asian "
        "professional prepare a formal partnership speech for a Malaysian university. "
        "The learner writes in English but understands Uzbek well; write your feedback "
        "in simple English with occasional short Uzbek clarifications in parentheses. "
        "Be concise: max 5 short lines. Point out grammar mistakes, then give one improved version."
    )
    user_message = (
        f'The learner was asked to write a sentence using this pattern: "{pattern}"\n\n'
        f'Their sentence: "{user_sentence}"\n\n'
        "Give brief, encouraging feedback and one corrected/improved version."
    )
    return await _ask(system, user_message, max_tokens=400)


async def review_speech(draft_text: str) -> str:
    system = (
        "You are an English speech coach helping a Central Asian education consultant "
        "polish a formal speech to deliver to a Malaysian university partner. "
        "Correct grammar and improve word choice while keeping the original meaning and tone. "
        "Write in simple, clear English with short Uzbek notes in parentheses for the key fixes. "
        "Structure your reply as:\n1) Corrected version\n2) 2-4 bullet points on what was fixed and why (short)."
    )
    return await _ask(system, draft_text, max_tokens=900)


async def generate_qa_questions(topic_hint: str) -> str:
    system = (
        "You generate realistic questions a Malaysian university partnership panel might "
        "ask an education consultant from Uzbekistan during a formal meeting. "
        "Return exactly 3 questions in English, numbered 1-3, each on its own line, no extra text."
    )
    user_message = f"Context: {topic_hint}. Generate 3 likely questions the panel might ask."
    return await _ask(system, user_message, max_tokens=250)


async def evaluate_qa_answer(question: str, user_answer: str) -> str:
    system = (
        "You are an English speaking coach evaluating a mock Q&A answer for a formal "
        "university partnership meeting. Be encouraging but honest. "
        "Write in simple English with short Uzbek notes in parentheses where helpful. "
        "Structure: 1) Quick assessment (1 line), 2) Grammar/wording fixes if any, "
        "3) One improved sample answer (2-3 sentences). Keep it under 8 lines total."
    )
    user_message = f'Question asked: "{question}"\n\nLearner\'s answer: "{user_answer}"'
    return await _ask(system, user_message, max_tokens=500)


async def evaluate_speaking(question: str, transcript: str, wpm: float, duration: float) -> str:
    system = (
        "You are an English speaking coach. You receive a speech-to-text transcript of a "
        "learner's SPOKEN answer, not written text — expect natural spoken patterns like "
        "filler words, repetition, or run-on sentences; this is normal in speech and should "
        "not be judged as harshly as written grammar. "
        "If part of the transcript seems garbled or nonsensical, gently note that unclear "
        "words might mean the pronunciation was hard for a listener to catch, rather than "
        "treating it purely as a grammar mistake. "
        "The learner is a Central Asian professional preparing a formal speech for a "
        "Malaysian university partnership meeting. "
        f"Their speaking rate was {wpm} words per minute (ideal for formal presentations is "
        "110-150 wpm — mention if they are too fast/slow). "
        "Give feedback in this structure: 1) Overall impression (1 line), 2) Grammar/wording "
        "issues found, 3) Pacing/fluency comment, 4) One specific tip to sound more natural. "
        "Write in simple English with short Uzbek clarifications in parentheses. "
        "Keep the whole answer under 9 lines, encouraging tone."
    )
    user_message = (
        f'Question asked: "{question}"\n\n'
        f'Transcribed spoken answer: "{transcript}"\n\n'
        f"Speaking rate: {wpm} wpm, duration: {duration:.0f} seconds."
    )
    return await _ask(system, user_message, max_tokens=550)
