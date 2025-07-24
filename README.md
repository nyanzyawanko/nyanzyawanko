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
if 'question_start_time' not in st.session_state:
    st.session_state.question_start_time = None

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
        op = random.choice(['+', '-', '*', '/'])
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
            a = random.randint(1, 25)
            b = random.randint(1, 25)
        elif difficulty == 'hard':
            a = random.randint(1, 50)
            b = random.randint(1, 50)
        else:  # expert
            a = random.randint(1, 100)
            b = random.randint(1, 100)
        question = f"{a} × {b}"
        answer = a * b
    elif op == '/':
        # 割り算は割り切れる問題のみ生成
        if difficulty == 'easy':
            # 初級: 1桁割る1桁 (2-9 ÷ 1-9)
            divisor = random.randint(2, 9)
            quotient = random.randint(1, 9)
            dividend = divisor * quotient
            question = f"{dividend} ÷ {divisor}"
            answer = quotient
        elif difficulty == 'medium':
            # 中級: 2桁割る1桁 (10-99 ÷ 2-9)
            divisor = random.randint(2, 9)
            quotient = random.randint(2, 15)  # 商が2桁にならないように調整
            dividend = divisor * quotient
            if dividend > 99:  # 2桁を超えた場合は調整
                quotient = random.randint(2, 99 // divisor)
                dividend = divisor * quotient
            question = f"{dividend} ÷ {divisor}"
            answer = quotient
        elif difficulty == 'hard':
            # 上級: 2桁割る2桁 (10-99 ÷ 10-99)
            divisor = random.randint(10, 20)  # 割る数を制限して計算しやすく
            quotient = random.randint(2, 9)   # 商を1桁に制限
            dividend = divisor * quotient
            if dividend > 99:  # 2桁を超えた場合は調整
                quotient = random.randint(2, 99 // divisor)
                dividend = divisor * quotient
            question = f"{dividend} ÷ {divisor}"
            answer = quotient
        else:  # expert
            # 超上級: より大きな数の割り算
            divisor = random.randint(11, 25)
            quotient = random.randint(5, 20)
            dividend = divisor * quotient
            question = f"{dividend} ÷ {divisor}"
            answer = quotient
        
    return question, answer

def start_game():
    """ゲームを開始する"""
    st.session_state.game_state = 'playing'
    st.session_state.score = 0
    st.session_state.question_count = 0
    st.session_state.start_time = time.time()
    st.session_state.history = []
    # 最初の問題を生成
    question, answer = generate_question(st.session_state.difficulty, st.session_state.operation)
    st.session_state.current_question = question
    st.session_state.current_answer = answer
    st.session_state.question_start_time = time.time()

def next_question():
    """次の問題に進む"""
    if st.session_state.question_count < st.session_state.total_questions:
        question, answer = generate_question(st.session_state.difficulty, st.session_state.operation)
        st.session_state.current_question = question
        st.session_state.current_answer = answer
        st.session_state.question_start_time = time.time()
    else:
        st.session_state.game_state = 'result'

def check_answer(user_answer):
    """回答をチェックする"""
    question_time = time.time() - st.session_state.question_start_time
    is_correct = user_answer == st.session_state.current_answer
    
    if is_correct:
        st.session_state.score += 1
        
    # 履歴に記録
    st.session_state.history.append({
        'question': st.session_state.current_question,
        'correct_answer': st.session_state.current_answer,
        'user_answer': user_answer,
        'is_correct': is_correct,
        'time': round(question_time, 2)
    })
    
    st.session_state.question_count += 1
    return is_correct, question_time

# メインのUI
st.title("🧮 高速暗算練習アプリ")

if st.session_state.game_state == 'menu':
    st.header("設定")
    
    col1, col2 = st.columns(2)
    
    with col1:
        difficulty = st.selectbox(
            "難易度を選択",
            ['easy', 'medium', 'hard', 'expert'],
            index=['easy', 'medium', 'hard', 'expert'].index(st.session_state.difficulty),
            format_func=lambda x: {'easy': '簡単 (1-20)', 'medium': '普通 (1-100)', 
                                  'hard': '難しい (10-500)', 'expert': '超難しい (50-1000)'}[x]
        )
        st.session_state.difficulty = difficulty
        
        operation = st.selectbox(
            "計算の種類",
            ['mixed', '+', '-', '*', '/'],
            index=['mixed', '+', '-', '*', '/'].index(st.session_state.operation),
            format_func=lambda x: {'mixed': 'ミックス', '+': '足し算', '-': '引き算', '*': 'かけ算', '/': '割り算'}[x]
        )
        st.session_state.operation = operation
    
    with col2:
        total_questions = st.number_input(
            "問題数",
            min_value=5,
            max_value=50,
            value=st.session_state.total_questions,
            step=5
        )
        st.session_state.total_questions = total_questions
    
    st.markdown("### 💡 割り算レベル説明")
    st.info("""
    **簡単**: 1桁割る1桁 (例: 8÷2, 18÷3)  
    **普通**: 2桁割る1桁 (例: 48÷6, 72÷8)  
    **難しい**: 2桁割る2桁 (例: 84÷12, 96÷16)  
    **超難しい**: より大きな数の割り算 (例: 225÷15, 360÷18)
    
    ※全て割り切れる問題のみ出題されます
    """)
    
    if st.button("🚀 ゲーム開始", type="primary", use_container_width=True):
        start_game()
        st.rerun()

elif st.session_state.game_state == 'playing':
    # プログレスバー
    progress = st.session_state.question_count / st.session_state.total_questions
    st.progress(progress)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.metric("問題", f"{st.session_state.question_count + 1}/{st.session_state.total_questions}")
    
    with col2:
        st.metric("正解数", st.session_state.score)
    
    with col3:
        elapsed_time = time.time() - st.session_state.start_time
        st.metric("経過時間", f"{elapsed_time:.1f}秒")
    
    st.markdown("---")
    
    # 問題表示
    st.markdown(f"### 問題: {st.session_state.current_question} = ?")
    
    # 回答入力
    with st.form("answer_form"):
        user_answer = st.number_input("答えを入力してください", step=1)
        submitted = st.form_submit_button("回答", type="primary", use_container_width=True)
        
        if submitted:
            is_correct, question_time = check_answer(int(user_answer))
            
            if is_correct:
                st.success(f"✅ 正解！ ({question_time:.2f}秒)")
            else:
                st.error(f"❌ 不正解。正解は {st.session_state.current_answer} でした。 ({question_time:.2f}秒)")
            
            time.sleep(1)  # 結果を表示する時間
            next_question()
            st.rerun()

elif st.session_state.game_state == 'result':
    st.header("🎉 結果発表")
    
    total_time = time.time() - st.session_state.start_time
    accuracy = (st.session_state.score / st.session_state.total_questions) * 100
    avg_time = sum([h['time'] for h in st.session_state.history]) / len(st.session_state.history)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("正解数", f"{st.session_state.score}/{st.session_state.total_questions}")
    
    with col2:
        st.metric("正答率", f"{accuracy:.1f}%")
    
    with col3:
        st.metric("総時間", f"{total_time:.1f}秒")
    
    with col4:
        st.metric("平均時間", f"{avg_time:.2f}秒/問")
    
    # パフォーマンス評価
    if accuracy >= 90 and avg_time <= 3:
        st.success("🏆 素晴らしい！暗算マスターです！")
    elif accuracy >= 80 and avg_time <= 5:
        st.info("👍 とても良い成績です！")
    elif accuracy >= 70:
        st.warning("📚 もう少し練習すれば上達しますよ！")
    else:
        st.error("💪 練習あるのみ！頑張りましょう！")
    
    st.markdown("---")
    
    # 詳細履歴
    st.subheader("📊 詳細履歴")
    
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        df['結果'] = df['is_correct'].map({True: '✅', False: '❌'})
        df = df[['question', 'user_answer', 'correct_answer', '結果', 'time']]
        df.columns = ['問題', 'あなたの答え', '正解', '結果', '時間(秒)']
        
        st.dataframe(df, use_container_width=True)
        
        # 統計情報
        st.subheader("📈 統計情報")
        correct_times = [h['time'] for h in st.session_state.history if h['is_correct']]
        incorrect_times = [h['time'] for h in st.session_state.history if not h['is_correct']]
        
        col1, col2 = st.columns(2)
        with col1:
            if correct_times:
                st.metric("正解時の平均時間", f"{sum(correct_times)/len(correct_times):.2f}秒")
        with col2:
            if incorrect_times:
                st.metric("不正解時の平均時間", f"{sum(incorrect_times)/len(incorrect_times):.2f}秒")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 もう一度挑戦", type="primary", use_container_width=True):
            start_game()
            st.rerun()
    
    with col2:
        if st.button("⚙️ 設定に戻る", use_container_width=True):
            st.session_state.game_state = 'menu'
            st.rerun()