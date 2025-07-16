import streamlit as st
import random
import time
from datetime import datetime, timedelta

# ページ設定
st.set_page_config(
    page_title="高速暗算アプリ",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS for styling
st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #1f77b4;
        font-size: 3em;
        margin-bottom: 0.5em;
    }
    .problem-display {
        font-size: 4em;
        text-align: center;
        margin: 1em 0;
        color: #2c3e50;
        font-weight: bold;
    }
    .timer-display {
        font-size: 2em;
        text-align: center;
        margin: 0.5em 0;
    }
    .timer-warning {
        color: #e74c3c;
        animation: blink 1s infinite;
    }
    .timer-normal {
        color: #27ae60;
    }
    .stats-box {
        padding: 1em;
        border-radius: 10px;
        margin: 0.5em 0;
        text-align: center;
    }
    .correct-answer {
        color: #27ae60;
        font-weight: bold;
        font-size: 1.5em;
    }
    .incorrect-answer {
        color: #e74c3c;
        font-weight: bold;
        font-size: 1.5em;
    }
    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0.3; }
    }
</style>
""", unsafe_allow_html=True)

# 演算設定（指定された条件通り）
OPERATIONS = {
    "足し算": {
        "symbol": "+",
        "levels": {
            "初級": {"digits": [1, 1], "time_limit": 5, "desc": "1桁+1桁"},
            "中級": {"digits": [2, 2], "time_limit": 15, "desc": "2桁+2桁"},
            "上級": {"digits": [3, 3], "time_limit": 25, "desc": "3桁+3桁"}
        }
    },
    "引き算": {
        "symbol": "-",
        "levels": {
            "初級": {"digits": [1, 1], "time_limit": 5, "desc": "1桁-1桁"},
            "中級": {"digits": [2, 2], "time_limit": 15, "desc": "2桁-2桁"},
            "上級": {"digits": [3, 3], "time_limit": 25, "desc": "3桁-3桁"}
        }
    },
    "掛け算": {
        "symbol": "×",
        "levels": {
            "初級": {"digits": [1, 1], "time_limit": 5, "desc": "1桁×1桁"},
            "中級": {"digits": [2, 1], "time_limit": 15, "desc": "2桁×1桁"},
            "上級": {"digits": [2, 2], "time_limit": 25, "desc": "2桁×2桁"}
        }
    },
    "割り算": {
        "symbol": "÷",
        "levels": {
            "初級": {"digits": [2, 1], "time_limit": 10, "desc": "2桁÷1桁"},
            "中級": {"digits": [3, 1], "time_limit": 20, "desc": "3桁÷1桁"},
            "上級": {"digits": [3, 2], "time_limit": 30, "desc": "3桁÷2桁"}
        }
    }
}

def generate_number(digits):
    """指定された桁数の数字を生成"""
    if digits == 1:
        return random.randint(1, 9)
    else:
        min_val = 10 ** (digits - 1)
        max_val = 10 ** digits - 1
        return random.randint(min_val, max_val)

def generate_problem(operation, level):
    """問題を生成"""
    config = OPERATIONS[operation]["levels"][level]
    digits = config["digits"]
    
    if operation == "足し算":
        num1 = generate_number(digits[0])
        num2 = generate_number(digits[1])
        answer = num1 + num2
    
    elif operation == "引き算":
        num1 = generate_number(digits[0])
        if digits[1] == 1:
            num2 = random.randint(1, min(9, num1))
        else:
            num2 = random.randint(1, num1)
        answer = num1 - num2
    
    elif operation == "掛け算":
        num1 = generate_number(digits[0])
        num2 = generate_number(digits[1])
        answer = num1 * num2
    
    elif operation == "割り算":
        num2 = generate_number(digits[1])  # 割る数
        quotient = generate_number(digits[0] - digits[1] + 1)  # 商
        num1 = num2 * quotient  # 割られる数
        answer = quotient
    
    return num1, num2, answer, config

# セッション状態の初期化
if 'game_state' not in st.session_state:
    st.session_state.game_state = 'menu'
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'total_problems' not in st.session_state:
    st.session_state.total_problems = 0
if 'streak' not in st.session_state:
    st.session_state.streak = 0
if 'best_streak' not in st.session_state:
    st.session_state.best_streak = 0
if 'current_problem' not in st.session_state:
    st.session_state.current_problem = None
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'feedback' not in st.session_state:
    st.session_state.feedback = ""
if 'feedback_type' not in st.session_state:
    st.session_state.feedback_type = ""

# メインタイトル
st.markdown('<h1 class="main-title">🧮 高速暗算アプリ</h1>', unsafe_allow_html=True)

# サイドバー設定
with st.sidebar:
    st.header("設定")
    
    # 演算選択
    operation = st.selectbox(
        "演算を選択",
        list(OPERATIONS.keys()),
        key="operation_select"
    )
    
    # 難易度選択
    level = st.selectbox(
        "難易度を選択",
        list(OPERATIONS[operation]["levels"].keys()),
        key="level_select"
    )
    
    # 選択した設定の表示
    config = OPERATIONS[operation]["levels"][level]
    st.info(f"""
    **選択された設定:**
    - 演算: {operation}
    - 難易度: {level}
    - 問題形式: {config['desc']}
    - 制限時間: {config['time_limit']}秒
    """)
    
    # 統計情報
    st.header("統計情報")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("正解数", st.session_state.score)
        st.metric("連続正解", st.session_state.streak)
    with col2:
        st.metric("総問題数", st.session_state.total_problems)
        st.metric("最高連続", st.session_state.best_streak)
    
    if st.session_state.total_problems > 0:
        accuracy = (st.session_state.score / st.session_state.total_problems) * 100
        st.metric("正解率", f"{accuracy:.1f}%")

# メイン画面
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.session_state.game_state == 'menu':
        st.markdown("### ゲームを開始する準備はできましたか？")
        st.markdown(f"**{operation} - {level}** ({config['desc']}, {config['time_limit']}秒)")
        
        if st.button("🎮 ゲーム開始", type="primary", use_container_width=True):
            st.session_state.game_state = 'playing'
            st.session_state.score = 0
            st.session_state.total_problems = 0
            st.session_state.streak = 0
            # 新しい問題を生成
            num1, num2, answer, config = generate_problem(operation, level)
            st.session_state.current_problem = {
                'num1': num1,
                'num2': num2,
                'answer': answer,
                'config': config,
                'operation': operation
            }
            st.session_state.start_time = time.time()
            st.session_state.feedback = ""
            st.rerun()
    
    elif st.session_state.game_state == 'playing':
        # 現在の問題を表示
        if st.session_state.current_problem:
            problem = st.session_state.current_problem
            symbol = OPERATIONS[problem['operation']]['symbol']
            
            # 残り時間計算
            elapsed_time = time.time() - st.session_state.start_time
            remaining_time = problem['config']['time_limit'] - elapsed_time
            
            # 問題表示
            st.markdown(f'<div class="problem-display">{problem["num1"]} {symbol} {problem["num2"]} = ?</div>', 
                       unsafe_allow_html=True)
            
            # タイマー表示
            if remaining_time > 0:
                timer_class = "timer-warning" if remaining_time <= 3 else "timer-normal"
                st.markdown(f'<div class="timer-display {timer_class}">⏰ {remaining_time:.1f}秒</div>', 
                           unsafe_allow_html=True)
                
                # 答え入力フォーム
                with st.form(key="answer_form", clear_on_submit=True):
                    user_answer = st.number_input("答えを入力してください", value=None, step=1, key="answer_input")
                    submitted = st.form_submit_button("回答 (Enter)", type="primary", use_container_width=True)
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if submitted and user_answer is not None:
                        # 答えをチェック
                        st.session_state.total_problems += 1
                        if user_answer == problem['answer']:
                            st.session_state.score += 1
                            st.session_state.streak += 1
                            st.session_state.best_streak = max(st.session_state.best_streak, st.session_state.streak)
                            st.session_state.feedback = "🎉 正解！"
                            st.session_state.feedback_type = "correct"
                        else:
                            st.session_state.streak = 0
                            st.session_state.feedback = f"❌ 不正解。正解は {problem['answer']} です。"
                            st.session_state.feedback_type = "incorrect"
                        
                        # 新しい問題を生成
                        num1, num2, answer, config = generate_problem(operation, level)
                        st.session_state.current_problem = {
                            'num1': num1,
                            'num2': num2,
                            'answer': answer,
                            'config': config,
                            'operation': operation
                        }
                        st.session_state.start_time = time.time()
                        st.rerun()
                
                with col_btn2:
                    if st.button("ゲーム終了", use_container_width=True):
                        st.session_state.game_state = 'menu'
                        st.session_state.feedback = ""
                        st.rerun()
                
                else:
                # 時間切れの場合
                st.session_state.total_problems += 1
                st.session_state.streak = 0
                st.session_state.feedback = f"⏰ 時間切れ！正解は {problem['answer']} です。"
                st.session_state.feedback_type = "incorrect"
                
                # フィードバック表示
                st.markdown(f'<div class="incorrect-answer">{st.session_state.feedback}</div>', 
                           unsafe_allow_html=True)
                
                # 次の問題ボタン
                if st.button("次の問題", type="primary", use_container_width=True):
                    num1, num2, answer, config = generate_problem(operation, level)
                    st.session_state.current_problem = {
                        'num1': num1,
                        'num2': num2,
                        'answer': answer,
                        'config': config,
                        'operation': operation
                    }
                    st.session_state.start_time = time.time()
                    st.session_state.feedback = ""
                    st.rerun()
            
            # フィードバック表示（時間切れ以外）
            if st.session_state.feedback and remaining_time > 0:
                if st.session_state.feedback_type == "correct":
                    st.markdown(f'<div class="correct-answer">{st.session_state.feedback}</div>', 
                               unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="incorrect-answer">{st.session_state.feedback}</div>', 
                               unsafe_allow_html=True)
            
            # 自動更新（1秒ごと）
            if remaining_time > 0:
                time.sleep(1)
                st.rerun()

# フッター
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>🎯 制限時間内に正確に計算しよう！</p>
    <p>各問題には制限時間が設定されています。時間内に正解を目指しましょう。</p>
</div>
""", unsafe_allow_html=True)
if submitted and user_answer is not None:
    try:
        user_answer = int(user_answer)
        ...
    except ValueError:
        st.warning("数値を入力してください。")
