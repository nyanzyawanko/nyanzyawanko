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
if 'difficulty' not in st.session_state:
    st.session_state.difficulty = 'medium'
if 'operation' not in st.session_state:
    st.session_state.operation = 'mixed'
if 'history' not in st.session_state:
    st.session_state.history = []

def generate_question(difficulty, operation):
    """問題を生成する関数"""
    if difficulty == 'easy':
        range_min, range_max = 1, 20
    elif difficulty == 'medium':
        range_min, range_max = 1, 100
    elif difficulty == 'hard':
        range_min, range_max = 10, 500
    else:  # expert
        range_min, range_max = 50, 1000
    
    if operation == 'mixed':
        op = random.choice(['+', '-', '*'])
    else:
        op = operation
    
    if op == '+':
        a = random.randint(range_min, range_max)
        b = random.randint(range_min, range_max)
        question = f"{a} + {b}"
        answer = a + b
    elif op == '-':
        a = random.randint(range_min, range_max)
        b = random.randint(range_min, a)  # 負の数を避ける
        question = f"{a} - {b}"
        answer = a - b
    elif op == '*':
        if difficulty == 'easy':
            a = random.randint(1, 12)
            b = random.randint(1, 12)
        elif difficulty == 'medium':
            a = random.randint(1, 20)
            b = random.randint(1, 20)
        else:
            a = random.randint(2, 50)
            b = random.randint(2, 50)
        question = f"{a} × {b}"
        answer = a * b
    
    return question, answer

def reset_game():
    """ゲームをリセットする関数"""
    st.session_state.game_state = 'menu'
    st.session_state.score = 0
    st.session_state.question_count = 0
    st.session_state.start_time = None
    st.session_state.current_question = None
    st.session_state.current_answer = None

def start_game():
    """ゲームを開始する関数"""
    st.session_state.game_state = 'playing'
    st.session_state.score = 0
    st.session_state.question_count = 0
    st.session_state.start_time = time.time()
    question, answer = generate_question(st.session_state.difficulty, st.session_state.operation)
    st.session_state.current_question = question
    st.session_state.current_answer = answer

def next_question():
    """次の問題に進む関数"""
    if st.session_state.question_count >= st.session_state.total_questions:
        st.session_state.game_state = 'finished'
        # 結果を履歴に追加
        end_time = time.time()
        total_time = end_time - st.session_state.start_time
        accuracy = (st.session_state.score / st.session_state.total_questions) * 100
        
        st.session_state.history.append({
            'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'difficulty': st.session_state.difficulty,
            'operation': st.session_state.operation,
            'score': st.session_state.score,
            'total': st.session_state.total_questions,
            'accuracy': f"{accuracy:.1f}%",
            'time': f"{total_time:.1f}秒",
            'avg_time': f"{total_time/st.session_state.total_questions:.1f}秒/問"
        })
    else:
        question, answer = generate_question(st.session_state.difficulty, st.session_state.operation)
        st.session_state.current_question = question
        st.session_state.current_answer = answer

# メインアプリケーション
st.title("🧮 高速暗算練習アプリ")

# サイドバー設定
with st.sidebar:
    st.header("⚙️ 設定")
    
    # 難易度設定
    difficulty_options = {
        'easy': '初級 (1-20)',
        'medium': '中級 (1-100)',
        'hard': '上級 (10-500)',
        'expert': '専門家 (50-1000)'
    }
    st.session_state.difficulty = st.selectbox(
        "難易度",
        options=list(difficulty_options.keys()),
        format_func=lambda x: difficulty_options[x],
        index=list(difficulty_options.keys()).index(st.session_state.difficulty)
    )
    
    # 演算設定
    operation_options = {
        'mixed': 'ミックス',
        '+': '足し算',
        '-': '引き算',
        '*': '掛け算'
    }
    st.session_state.operation = st.selectbox(
        "演算種類",
        options=list(operation_options.keys()),
        format_func=lambda x: operation_options[x],
        index=list(operation_options.keys()).index(st.session_state.operation)
    )
    
    # 問題数設定
    st.session_state.total_questions = st.slider(
        "問題数",
        min_value=5,
        max_value=50,
        value=st.session_state.total_questions,
        step=5
    )
    
    st.divider()
    
    # ゲームリセット
    if st.button("🔄 リセット"):
        reset_game()
        st.rerun()

# メインコンテンツ
if st.session_state.game_state == 'menu':
    st.header("🎯 ゲームスタート")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **現在の設定:**
        - 難易度: {difficulty_options[st.session_state.difficulty]}
        - 演算: {operation_options[st.session_state.operation]}
        - 問題数: {st.session_state.total_questions}問
        """)
    
    with col2:
        st.success("""
        **遊び方:**
        1. 設定を確認してスタートボタンを押す
        2. 表示された問題を暗算で解く
        3. 答えを入力してEnterを押す
        4. 制限時間内にできるだけ多く正解しよう！
        """)
    
    if st.button("🚀 ゲームスタート", type="primary", use_container_width=True):
        start_game()
        st.rerun()

elif st.session_state.game_state == 'playing':
    # 進捗表示
    progress = st.session_state.question_count / st.session_state.total_questions
    st.progress(progress)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("問題", f"{st.session_state.question_count + 1}/{st.session_state.total_questions}")
    with col2:
        st.metric("正解数", st.session_state.score)
    with col3:
        if st.session_state.start_time:
            elapsed = time.time() - st.session_state.start_time
            st.metric("経過時間", f"{elapsed:.1f}秒")
    
    st.divider()
    
    # 問題表示
    st.header("💡 問題")
    st.subheader(f"**{st.session_state.current_question} = ?**")
    
    # 答え入力
    user_answer = st.number_input(
        "答えを入力してください:",
        value=0,
        step=1,
        key=f"answer_{st.session_state.question_count}"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ 答える", type="primary"):
            st.session_state.question_count += 1
            if user_answer == st.session_state.current_answer:
                st.session_state.score += 1
                st.success(f"正解！ 答えは {st.session_state.current_answer} です")
            else:
                st.error(f"不正解... 正解は {st.session_state.current_answer} です")
            
            time.sleep(1)
            next_question()
            st.rerun()
    
    with col2:
        if st.button("⏭️ スキップ"):
            st.session_state.question_count += 1
            st.warning(f"スキップしました。答えは {st.session_state.current_answer} です")
            time.sleep(1)
            next_question()
            st.rerun()

elif st.session_state.game_state == 'finished':
    st.header("🎉 ゲーム終了!")
    
    # 結果表示
    accuracy = (st.session_state.score / st.session_state.total_questions) * 100
    total_time = time.time() - st.session_state.start_time
    avg_time = total_time / st.session_state.total_questions
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("正解数", f"{st.session_state.score}/{st.session_state.total_questions}")
    with col2:
        st.metric("正答率", f"{accuracy:.1f}%")
    with col3:
        st.metric("総時間", f"{total_time:.1f}秒")
    with col4:
        st.metric("平均時間", f"{avg_time:.1f}秒/問")
    
    # 評価
    if accuracy >= 90:
        st.success("🏆 素晴らしい！完璧に近い成績です！")
    elif accuracy >= 70:
        st.info("👍 良い成績です！もう少しで完璧です！")
    elif accuracy >= 50:
        st.warning("📚 もう少し練習が必要ですね。")
    else:
        st.error("💪 諦めずに練習を続けましょう！")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 もう一度プレイ", type="primary"):
            start_game()
            st.rerun()
    
    with col2:
        if st.button("📋 メニューに戻る"):
            reset_game()
            st.rerun()

# 履歴表示
if st.session_state.history:
    st.divider()
    st.header("📊 練習履歴")
    
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df, use_container_width=True)
    
    # 統計情報
    if len(st.session_state.history) > 1:
        col1, col2 = st.columns(2)
        with col1:
            avg_accuracy = df['accuracy'].str.rstrip('%').astype(float).mean()
            st.metric("平均正答率", f"{avg_accuracy:.1f}%")
        
        with col2:
            total_games = len(st.session_state.history)
            st.metric("総プレイ回数", f"{total_games}回")
