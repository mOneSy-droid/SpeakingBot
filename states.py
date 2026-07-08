from aiogram.fsm.state import State, StatesGroup


class PracticeStates(StatesGroup):
    waiting_for_sentence = State()


class SpeechStates(StatesGroup):
    waiting_for_draft = State()


class QAStates(StatesGroup):
    waiting_for_answer = State()


class SpeakingStates(StatesGroup):
    waiting_for_voice = State()
