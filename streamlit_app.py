import random
import time
import streamlit as st

# ページ設定
st.set_page_config(
    page_title="高速暗算練習アプリ",
    page_icon="🧮",
    layout="wide"
)

# セッション状態の初期化
if 'game_state' not in st.session_state:
    st.session_state.game_state = 'menu'
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'question_count' not in st.session_state:
    st.session_state.question_count = 0
if 'total_questions' not in st.session_state:
    st.session_state.total_questions = 10
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'current_question' not in st.session_state:
    st.session_state.current_question = None
if 'current_answer' not in st.session_state:
    st.session_state.current_answer = None
if 'operation' not in st.session_state:
    st.session_state.operation = 'mixed'
if 'history' not in st.session_state:
    st.session_state.history = []
if 'question_start_time' not in st.session_state:
    st.session_state.question_start_time = None
if 'current_streak' not in st.session_state:
    st.session_state.current_streak = 0
if 'max_streak' not in st.session_state:
    st.session_state.max_streak = 0
if 'all_time_best_streak' not in st.session_state:
    st.session_state.all_time_best_streak = 0
if 'game_mode' not in st.session_state:
    st.session_state.game_mode = 'normal'
if 'time_attack_duration' not in st.session_state:
    st.session_state.time_attack_duration = 60
if 'question_time_limit' not in st.session_state:
    st.session_state.question_time_limit = None
if 'time_limit_exceeded' not in st.session_state:
    st.session_state.time_limit_exceeded = False

# カスタム設定の初期化
if 'custom_settings' not in st.session_state:
    st.session_state.custom_settings = {
        'addition': {
            'min_digits_a': 1,
            'max_digits_a': 2,
            'min_digits_b': 1,
            'max_digits_b': 2,
            'time_limit': None
        },
        'subtraction': {
            'min_digits_a': 1,
            'max_digits_a': 2,
            'min_digits_b': 1,
            'max_digits_b': 2,
            'time_limit': None
        },
        'multiplication': {
            'min_digits_a': 1,
            'max_digits_a': 2,
            'min_digits_b': 1,
            'max_digits_b': 2,
            'time_limit': None
        },
        'division': {
            'min_digits_dividend': 1,
            'max_digits_dividend': 2,
            'min_digits_divisor': 1,
            'max_digits_divisor': 1,
            'time_limit': 20
        }
    }

def generate_number_by_digits(min_digits, max_digits):
    """指定された桁数の範囲で数値を生成"""
    digits = random.randint(min_digits, max_digits)
    if digits == 1:
        return random.randint(1, 9)
    else:
        min_val = 10 ** (digits - 1)
        max_val = (10 ** digits) - 1
        return random.randint(min_val, max_val)

def is_question_time_up():
    """問題ごとの制限時間をチェック"""
    if (st.session_state.question_time_limit and 
        st.session_state.question_start_time):
        elapsed = time.time() - st.session_state.question_start_time
        return elapsed >= st.session_state.question_time_limit
    return False

def is_time_up():
    """タイムアタックモードで時間切れかチェック"""
    if st.session_state.game_mode == 'time_attack' and st.session_state.start_time:
        elapsed = time.time() - st.session_state.start_time
        return elapsed >= st.session_state.time_attack_duration
    return False

def generate_question_custom(operation):
    """カスタム設定に基づいて問題を生成"""
    if operation == 'mixed':
        op = random.choice(['+', '-', '*', '/'])
    else:
        op = operation
    
    if op == '+':
        s = st.session_state.custom_settings['addition']
        a = generate_number_by_digits(s['min_digits_a'], s['max_digits_a'])
        b = generate_number_by_digits(s['min_digits_b'], s['max_digits_b'])
        question = f"{a} + {b}"
        answer = a + b
        time_limit = s['time_limit']
    elif op == '-':
        s = st.session_state.custom_settings['subtraction']
        a = generate_number_by_digits(s['min_digits_a'], s['max_digits_a'])
        b = generate_number_by_digits(s['min_digits_b'], s['max_digits_b'])
        if b > a:
            a, b = b, a
        question = f"{a} - {b}"
        answer = a - b
        time_limit = s['time_limit']
    elif op == '*':
        s = st.session_state.custom_settings['multiplication']
        a = generate_number_by_digits(s['min_digits_a'], s['max_digits_a'])
        b = generate_number_by_digits(s['min_digits_b'], s['max_digits_b'])
        question = f"{a} × {b}"
        answer = a * b
        time_limit = s['time_limit']
    elif op == '/':
        s = st.session_state.custom_settings['division']
        divisor = generate_number_by_digits(s['min_digits_divisor'], s['max_digits_divisor'])
        quotient_digits = s['max_digits_dividend'] - s['min_digits_divisor'] + 1
        quotient_digits = max(1, min(quotient_digits, 3))
        quotient = generate_number_by_digits(1, quotient_digits)
        dividend = divisor * quotient
        min_dividend = 10 ** (s['min_digits_dividend'] - 1) if s['min_digits_dividend'] > 1 else 1
        max_dividend = (10 ** s['max_digits_dividend']) - 1
        if dividend < min_dividend or dividend > max_dividend:
            min_q = max(1, min_dividend // divisor)
            max_q = max_dividend // divisor
            if max_q >= min_q:
                quotient = random.randint(min_q, max_q)
                dividend = divisor * quotient
            else:
                divisor = random.randint(2, max_dividend // 2)
                quotient = random.randint(1, max_dividend // divisor)
                dividend = divisor * quotient
        question = f"{dividend} ÷ {divisor}"
        answer = quotient
        time_limit = s['time_limit']
    else:
        question = "?"
        answer = None
        time_limit = None
    return question, answer, time_limit

def start_game():
    st.session_state.game_state = 'playing'
    st.session_state.score = 0
    st.session_state.question_count = 0
    st.session_state.start_time = time.time()
    st.session_state.history = []
    st.session_state.current_streak = 0
    st.session_state.max_streak = 0
    st.session_state.time_limit_exceeded = False

    q, a, tl = generate_question_custom(st.session_state.operation)
    st.session_state.current_question = q
    st.session_state.current_answer = a
    st.session_state.question_time_limit = tl
    st.session_state.question_start_time = time.time()

def next_question():
    if is_time_up():
        st.session_state.game_state = 'result'
        return
    if st.session_state.game_mode == 'normal' and st.session_state.question_count >= st.session_state.total_questions:
        st.session_state.game_state = 'result'
        return
    q, a, tl = generate_question_custom(st.session_state.operation)
    st.session_state.current_question = q
    st.session_state.current_answer = a
    st.session_state.question_time_limit = tl
    st.session_state.question_start_time = time.time()
    st.session_state.time_limit_exceeded = False

def check_answer(user_answer):
    question_time = time.time() - st.session_state.question_start_time
    is_correct = user_answer == st.session_state.current_answer
    time_limit_exceeded = is_question_time_up()

    if time_limit_exceeded:
        is_correct = False
        st.session_state.time_limit_exceeded = True

    if is_correct:
        st.session_state.score += 1
        st.session_state.current_streak += 1
        if st.session_state.current_streak > st.session_state.max_streak:
            st.session_state.max_streak = st.session_state.current_streak
        if st.session_state.current_streak > st.session_state.all_time_best_streak:
            st.session_state.all_time_best_streak = st.session_state.current_streak
    else:
        st.session_state.current_streak = 0

    st.session_state.history.append({
        'question': st.session_state.current_question,
        'correct_answer': st.session_state.current_answer,
        'user_answer': user_answer,
        'is_correct': is_correct,
        'time': round(question_time, 2),
        'streak_at_time': st.session_state.current_streak if is_correct else 0,
        '
