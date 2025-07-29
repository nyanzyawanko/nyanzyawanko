import streamlit as st
import random
import time
import pandas as pd
from datetime import datetime

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

def get_question_remaining_time():
    """問題ごとの残り時間を取得"""
    if (st.session_state.question_time_limit and 
        st.session_state.question_start_time):
        elapsed = time.time() - st.session_state.question_start_time
        remaining = max(0, st.session_state.question_time_limit - elapsed)
        return remaining
    return None

def is_time_up():
    """タイムアタックモードで時間切れかチェック"""
    if st.session_state.game_mode == 'time_attack' and st.session_state.start_time:
        elapsed = time.time() - st.session_state.start_time
        return elapsed >= st.session_state.time_attack_duration
    return False

def get_remaining_time():
    """タイムアタックモードでの残り時間を取得"""
    if st.session_state.game_mode == 'time_attack' and st.session_state.start_time:
        elapsed = time.time() - st.session_state.start_time
        remaining = max(0, st.session_state.time_attack_duration - elapsed)
        return remaining
    return None

def generate_question_custom(operation):
    """カスタム設定に基づいて問題を生成する関数"""
    if operation == 'mixed':
        op = random.choice(['+', '-', '*', '/'])
    else:
        op = operation
    
    if op == '+':
        settings = st.session_state.custom_settings['addition']
        a = generate_number_by_digits(settings['min_digits_a'], settings['max_digits_a'])
        b = generate_number_by_digits(settings['min_digits_b'], settings['max_digits_b'])
        question = f"{a} + {b}"
        answer = a + b
        time_limit = settings['time_limit']
        
    elif op == '-':
        settings = st.session_state.custom_settings['subtraction']
        a = generate_number_by_digits(settings['min_digits_a'], settings['max_digits_a'])
        b = generate_number_by_digits(settings['min_digits_b'], settings['max_digits_b'])
        # 負の数を避ける
        if b > a:
            a, b = b, a
        question = f"{a} - {b}"
        answer = a - b
        time_limit = settings['time_limit']
        
    elif op == '*':
        settings = st.session_state.custom_settings['multiplication']
        a = generate_number_by_digits(settings['min_digits_a'], settings['max_digits_a'])
        b = generate_number_by_digits(settings['min_digits_b'], settings['max_digits_b'])
        question = f"{a} × {b}"
        answer = a * b
        time_limit = settings['time_limit']
        
    elif op == '/':
        settings = st.session_state.custom_settings['division']
        # 割り切れる問題のみ生成
        divisor = generate_number_by_digits(settings['min_digits_divisor'], settings['max_digits_divisor'])
        quotient_digits = settings['max_digits_dividend'] - settings['min_digits_divisor'] + 1
        quotient_digits = max(1, min(quotient_digits, 3))  # 商の桁数を制限
        quotient = generate_number_by_digits(1, quotient_digits)
        dividend = divisor * quotient
        
        # 指定された桁数範囲に収まるように調整
        min_dividend = 10 ** (settings['min_digits_dividend'] - 1) if settings['min_digits_dividend'] > 1 else 1
        max_dividend = (10 ** settings['max_digits_dividend']) - 1
        
        # 範囲外の場合は再生成
        if dividend < min_dividend or dividend > max_dividend:
            # 範囲内に収まるように商を調整
            min_quotient = max(1, min_dividend // divisor)
            max_quotient = max_dividend // divisor
            if max_quotient >= min_quotient:
                quotient = random.randint(min_quotient, max_quotient)
                dividend = divisor * quotient
            else:
                # 調整できない場合は除数を変更
                divisor = random.randint(2, max_dividend // 2)
                quotient = random.randint(1, max_dividend // divisor)
                dividend = divisor * quotient
        
        question = f"{dividend} ÷ {divisor}"
        answer = quotient
        time_limit = settings['time_limit']
    
    return question, answer, time_limit

def start_game():
    """ゲームを開始する"""
    st.session_state.game_state = 'playing'
    st.session_state.score = 0
    st.session_state.question_count = 0
    st.session_state.start_time = time.time()
    st.session_state.history = []
    st.session_state.current_streak = 0
    st.session_state.max_streak = 0
    st.session_state.time_limit_exceeded = False
    
    # 最初の問題を生成
    question, answer, time_limit = generate_question_custom(st.session_state.operation)
    st.session_state.current_question = question
    st.session_state.current_answer = answer
    st.session_state.question_time_limit = time_limit
    st.session_state.question_start_time = time.time()

def next_question():
    """次の問題に進む"""
    # タイムアタックモードで時間切れチェック
    if is_time_up():
        st.session_state.game_state = 'result'
        return
    
    # 通常モードでは問題数をチェック
    if st.session_state.game_mode == 'normal' and st.session_state.question_count >= st.session_state.total_questions:
        st.session_state.game_state = 'result'
        return
    
    # 次の問題を生成
    question, answer, time_limit = generate_question_custom(st.session_state.operation)
    st.session_state.current_question = question
    st.session_state.current_answer = answer
    st.session_state.question_time_limit = time_limit
    st.session_state.question_start_time = time.time()
    st.session_state.time_limit_exceeded = False

def check_answer(user_answer):
    """回答をチェックする"""
    question_time = time.time() - st.session_state.question_start_time
    is_correct = user_answer == st.session_state.current_answer
    time_limit_exceeded = is_question_time_up()
    
    # 制限時間オーバーの場合は不正解扱い
    if time_limit_exceeded:
        is_correct = False
        st.session_state.time_limit_exceeded = True
    
    if is_correct:
        st.session_state.score += 1
        st.session_state.current_streak += 1
        # 現在のゲームでの最高記録を更新
        if st.session_state.current_streak > st.session_state.max_streak:
            st.session_state.max_streak = st.session_state.current_streak
        # 全時間での最高記録を更新
        if st.session_state.current_streak > st.session_state.all_time_best_streak:
            st.session_state.all_time_best_streak = st.session_state.current_streak
    else:
        st.session_state.current_streak = 0
        
    # 履歴に記録
    st.session_state.history.append({
        'question': st.session_state.current_question,
        'correct_answer': st.session_state.current_answer,
        'user_answer': user_answer,
        'is_correct': is_correct,
        'time': round(question_time, 2),
        'streak_at_time': st.session_state.current_streak if is_correct else 0,
        'time_limit_exceeded': time_limit_exceeded
    })
    
    st.session_state.question_count += 1
    return is_correct, question_time, time_limit_exceeded

# メインのUI
st.title("🧮 高速暗算練習アプリ")

if st.session_state.game_state == 'menu':
    st.header("設定")
    
    # タブで設定を分ける
    tab1, tab2 = st.tabs(["🎮 基本設定", "⚙️ 詳細設定"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎮 ゲームモード")
            game_mode = st.radio(
                "モードを選択",
                ['normal', 'time_attack'],
                index=['normal', 'time_attack'].index(st.session_state.game_mode),
                format_func=lambda x: {'normal': '📚 通常モード（問題数指定）', 'time_attack': '⏱️ タイムアタック'}[x]
            )
            st.session_state.game_mode = game_mode
            
            if game_mode == 'normal':
                total_questions = st.number_input(
                    "問題数",
                    min_value=5,
                    max_value=100,
                    value=st.session_state.total_questions,
                    step=5
                )
                st.session_state.total_questions = total_questions
            else:
                time_attack_duration = st.number_input(
                    "制限時間（秒）",
                    min_value=30,
                    max_value=300,
                    value=st.session_state.time_attack_duration,
                    step=10
                )
                st.session_state.time_attack_duration = time_attack_duration
        
        with col2:
            st.subheader("📝 計算の種類")
            operation = st.selectbox(
                "計算の種類",
                ['mixed', '+', '-', '*', '/'],
                index=['mixed', '+', '-', '*', '/'].index(st.session_state.operation),
                format_func=lambda x: {'mixed': 'ミックス', '+': '足し算', '-': '引き算', '*': 'かけ算', '/': '割り算'}[x]
            )
            st.session_state.operation = operation
    
    with tab2:
        st.subheader("🔧 詳細設定")
        st.info("各計算の桁数と制限時間をカスタマイズできます")
        
        # 足し算設定
        with st.expander("➕ 足し算設定", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.session_state.custom_settings['addition']['min_digits_a'] = st.number_input(
                    "第1項 最小桁数", min_value=1, max_value=5, 
                    value=st.session_state.custom_settings['addition']['min_digits_a'],
                    key="add_min_a"
                )
                st.session_state.custom_settings['addition']['max_digits_a'] = st.number_input(
                    "第1項 最大桁数", min_value=1, max_value=5,
                    value=st.session_state.custom_settings['addition']['max_digits_a'],
                    key="add_max_a"
                )
            with col2:
                st.session_state.custom_settings['addition']['min_digits_b'] = st.number_input(
                    "第2項 最小桁数", min_value=1, max_value=5,
                    value=st.session_state.custom_settings['addition']['min_digits_b'],
                    key="add_min_b"
                )
                st.session_state.custom_settings['addition']['max_digits_b'] = st.number_input(
                    "第2項 最大桁数", min_value=1, max_value=5,
                    value=st.session_state.custom_settings['addition']['max_digits_b'],
                    key="add_max_b"
                )
            with col3:
                enable_time_limit = st.checkbox("制限時間を設定", key="add_time_enable")
                if enable_time_limit:
                    st.session_state.custom_settings['addition']['time_limit'] = st.number_input(
                        "制限時間（秒）", min_value=1, max_value=120,
                        value=st.session_state.custom_settings['addition']['time_limit'] or 10,
                        key="add_time_limit"
                    )
                else:
                    st.session_state.custom_settings['addition']['time_limit'] = None
        
        # 引き算設定
        with st.expander("➖ 引き算設定", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.session_state.custom_settings['subtraction']['min_digits_a'] = st.number_input(
                    "被減数 最小桁数", min_value=1, max_value=5, 
                    value=st.session_state.custom_settings['subtraction']['min_digits_a'],
                    key="sub_min_a"
                )
                st.session_state.custom_settings['subtraction']['max_digits_a'] = st.number_input(
                    "被減数 最大桁数", min_value=1, max_value=5,
                    value=st.session_state.custom_settings['subtraction']['max_digits_a'],
                    key="sub_max_a"
                )
            with col2:
                st.session_state.custom_settings['subtraction']['min_digits_b'] = st.number_input(
                    "減数 最小桁数", min_value=1, max_value=5,
                    value=st.session_state.custom_settings['subtraction']['min_digits_b'],
                    key="sub_min_b"
                )
                st.session_state.custom_settings['subtraction']['max_digits_b'] = st.number_input(
                    "減数 最大桁数", min_value=1, max_value=5,
                    value=st.session_state.custom_settings['subtraction']['max_digits_b'],
                    key="sub_max_b"
                )
            with col3:
                enable_time_limit = st.checkbox("制限時間を設定", key="sub_time_enable")
                if enable_time_limit:
                    st.session_state.custom_settings['subtraction']['time_limit'] = st.number_input(
                        "制限時間（秒）", min_value=1, max_value=120,
                        value=st.session_state.custom_settings['subtraction']['time_limit'] or 10,
                        key="sub_time_limit"
                    )
                else:
                    st.session_state.custom_settings['subtraction']['time_limit'] = None
        
        # かけ算設定
        with st.expander("✖️ かけ算設定", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.session_state.custom_settings['multiplication']['min_digits_a'] = st.number_input(
                    "第1項 最小桁数", min_value=1, max_value=4, 
                    value=st.session_state.custom_settings['multiplication']['min_digits_a'],
                    key="mul_min_a"
                )
                st.session_state.custom_settings['multiplication']['max_digits_a'] = st.number_input(
                    "第1項 最大桁数", min_value=1, max_value=4,
                    value=st.session_state.custom_settings['multiplication']['max_digits_a'],
                    key="mul_max_a"
                )
            with col2:
                st.session_state.custom_settings['multiplication']['min_digits_b'] = st.number_input(
                    "第2項 最小桁数", min_value=1, max_value=4,
                    value=st.session_state.custom_settings['multiplication']['min_digits_b'],
                    key="mul_min_b"
                )
                st.session_state.custom_settings['multiplication']['max_digits_b'] = st.number_input(
                    "第2項 最大桁数", min_value=1, max_value=4,
                    value=st.session_state.custom_settings['multiplication']['max_digits_b'],
                    key="mul_max_b"
                )
            with col3:
                enable_time_limit = st.checkbox("制限時間を設定", key="mul_time_enable")
                if enable_time_limit:
                    st.session_state.custom_settings['multiplication']['time_limit'] = st.number_input(
                        "制限時間（秒）", min_value=1, max_value=120,
                        value=st.session_state.custom_settings['multiplication']['time_limit'] or 15,
                        key="mul_time_limit"
                    )
                else:
                    st.session_state.custom_settings['multiplication']['time_limit'] = None
        
        # 割り算設定
        with st.expander("➗ 割り算設定", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.session_state.custom_settings['division']['min_digits_dividend'] = st.number_input(
                    "被除数 最小桁数", min_value=1, max_value=4, 
                    value=st.session_state.custom_settings['division']['min_digits_dividend'],
                    key="div_min_dividend"
                )
                st.session_state.custom_settings['division']['max_digits_dividend'] = st.number_input(
                    "被除数 最大桁数", min_value=1, max_value=4,
                    value=st.session_state.custom_settings['division']['max_digits_dividend'],
                    key="div_max_dividend"
                )
            with col2:
                st.session_state.custom_settings['division']['min_digits_divisor'] = st.number_input(
                    "除数 最小桁数", min_value=1, max_value=3,
                    value=st.session_state.custom_settings['division']['min_digits_divisor'],
                    key="div_min_divisor"
                )
                st.session_state.custom_settings['division']['max_digits_divisor'] = st.number_input(
                    "除数 最大桁数", min_value=1, max_value=3,
                    value=st.session_state.custom_settings['division']['max_digits_divisor'],
                    key="div_max_divisor"
                )
            with col3:
                enable_time_limit = st.checkbox("制限時間を設定", value=True, key="div_time_enable")
                if enable_time_limit:
                    st.session_state.custom_settings['division']['time_limit'] = st.number_input(
                        "制限時間（秒）", min_value=1, max_value=120,
                        value=st.session_state.custom_settings['division']['time_limit'] or 20,
                        key="div_time_limit"
                    )
                else:
                    st.session_state.custom_settings['division']['time_limit'] = None
            
            st.info("💡 割り算は全て割り切れる問題のみ出題されます")
        
        # プリセット設定
        st.subheader("🎯 プリセット設定")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🟢 初級レベル", use_container_width=True):
                st.session_state.custom_settings = {
                    'addition': {'min_digits_a': 1, 'max_digits_a': 1, 'min_digits_b': 1, 'max_digits_b': 1, 'time_limit': None},
                    'subtraction': {'min_digits_a': 1, 'max_digits_a': 2, 'min_digits_b': 1, 'max_digits_b': 1, 'time_limit': None},
                    'multiplication': {'min_digits_a': 1, 'max_digits_a': 1, 'min_digits_b': 1, 'max_digits_b': 1, 'time_limit': None},
                    'division': {'min_digits_dividend': 1, 'max_digits_dividend': 2, 'min_digits_divisor': 1, 'max_digits_divisor': 1, 'time_limit': 10}
                }
                st.success("初級レベルに設定しました！")
                st.rerun()
        
        with col2:
            if st.button("🟡 中級レベル", use_container_width=True):
                st.session_state.custom_settings = {
                    'addition': {'min_digits_a': 1, 'max_digits_a': 2, 'min_digits_b': 1, 'max_digits_b': 2, 'time_limit': None},
                    'subtraction': {'min_digits_a': 2, 'max_digits_a': 2, 'min_digits_b': 1, 'max_digits_b': 2, 'time_limit': None},
                    'multiplication': {'min_digits_a': 1, 'max_digits_a': 2, 'min_digits_b': 1, 'max_digits_b': 2, 'time_limit': None},
                    'division': {'min_digits_dividend': 2, 'max_digits_dividend': 2, 'min_digits_divisor': 1, 'max_digits_divisor': 1, 'time_limit': 20}
                }
                st.success("中級レベルに設定しました！")
                st.rerun()
        
        with col3:
            if st.button("🟠 上級レベル", use_container_width=True):
                st.session_state.custom_settings = {
                    'addition': {'min_digits_a': 2, 'max_digits_a': 3, 'min_digits_b': 2, 'max_digits_b': 3, 'time_limit': 15},
                    'subtraction': {'min_digits_a': 2, 'max_digits_a': 3, 'min_digits_b': 2, 'max_digits_b': 3, 'time_limit': 15},
                    'multiplication': {'min_digits_a': 2, 'max_digits_a': 2, 'min_digits_b': 1, 'max_digits_b': 2, 'time_limit': 20},
                    'division': {'min_digits_dividend': 2, 'max_digits_dividend': 3, 'min_digi