"""FSM holatlari — Quiz jarayoni"""
from aiogram.fsm.state import State, StatesGroup


class QuizStates(StatesGroup):
    choosing_subject = State()      # Fan tanlash
    choosing_mode = State()         # Rejim: mavzu/aralash
    choosing_topic = State()        # Mavzu tanlash
    choosing_count = State()        # Savol soni
    choosing_order = State()        # Tartib: ketma-ket/aralash
    choosing_time = State()         # Vaqt chegarasi
    choosing_skip_limit = State()   # O'tkazish limiti
    in_quiz = State()               # Test jarayonida
    quiz_paused = State()           # 3 ta skip — to'xtatilgan
