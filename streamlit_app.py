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
if 'current_streak' not in st.session_state:
    st.session_state.current_streak = 0
if 'max_streak' not in st.session_state:
    st.session_state.max_streak = 0
if 'all_time_best_streak' not in st.session_state:
    st.session_state.all_time_best_streak = 0
if 'game_mode' not in st.session_state:
    st.session_state.game_mode = 'normal'  # 'normal' or 'time_attack'
if 'time_attack_duration' not in st.session_state:
    st.session_state.time_attack_duration = 60  # 60秒
if 'question_time_limit' not in st.session_state:
    st.session_state.question_time_limit = None  # 問題ごとの制限時間
if 'time_limit_exceeded' not in st.session_state:
    st.session_state.time_limit_exceeded = False

def get_question_time_limit(difficulty, operation):
    """割り算モードの場合、難易度に応じた制限時間を返す"""
    if operation == '/' or (operation == 'mixed' and '/' in ['+', '-', '*', '/']):
        if difficulty == 'easy':
            return 10  # 初級: 10秒
        elif difficulty == 'medium':
            return 20  # 中級: 20秒
        elif difficulty == 'hard':
            return 30  # 上級: 30秒
        else:  # expert
            return 40  # 超上級: 40秒
    return None  # 割り算以外は制限時間なし

def is_question_time_up():
    """問題ごとの制限時間をチェック"""
    if (st.session_state.question_time_limit and 
        st.session_state.question_start_time and 
        (st.session_state.operation == '/' or st.session_state.operation == 'mixed')):
        elapsed = time.time() - st.session_state.question_start_time
        return elapsed >= st.session_state.question_time_limit
    return False

def get_question_remaining_time():
    """問題ごとの残り時間を取得"""
    if (st.session_state.question_time_limit and 
        st.session_state.question_start_time and
        (st.session_state.operation == '/' or st.session_state.operation == 'mixed')):
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
    st.session_state.current_streak = 0
    st.session_state.max_streak = 0
    st.session_state.time_limit_exceeded = False
    
    # 割り算モードの制限時間を設定
    st.session_state.question_time_limit = get_question_time_limit(
        st.session_state.difficulty, st.session_state.operation
    )
    
    # 最初の問題を生成
    question, answer = generate_question(st.session_state.difficulty, st.session_state.operation)
    st.session_state.current_question = question
    st.session_state.current_answer = answer
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
    question, answer = generate_question(st.session_state.difficulty, st.session_state.operation)
    st.session_state.current_question = question
    st.session_state.current_answer = answer
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
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎮 ゲームモード")
        game_mode = st.radio(
            "モードを選択",
            ['normal', 'time_attack'],
            index=['normal', 'time_attack'].index(st.session_state.game_mode),
            format_func=lambda x: {'normal': '📚 通常モード（問題数指定）', 'time_attack': '⏱️ タイムアタック（1分間）'}[x]
        )
        st.session_state.game_mode = game_mode
        
        if game_mode == 'normal':
            total_questions = st.number_input(
                "問題数",
                min_value=5,
                max_value=50,
                value=st.session_state.total_questions,
                step=5
            )
            st.session_state.total_questions = total_questions
        else:
            st.info("⏱️ **1分間で何問解けるかチャレンジ！**")
    
    with col2:
        st.subheader("⚙️ 設定")
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
    
    st.markdown("### 💡 割り算レベル説明")
    st.info("""
    **簡単**: 1桁割る1桁 (例: 8÷2, 18÷3) - ⏰ **制限時間: 10秒**  
    **普通**: 2桁割る1桁 (例: 48÷6, 72÷8) - ⏰ **制限時間: 20秒**  
    **難しい**: 2桁割る2桁 (例: 84÷12, 96÷16) - ⏰ **制限時間: 30秒**  
    **超難しい**: より大きな数の割り算 (例: 225÷15, 360÷18) - ⏰ **制限時間: 40秒**
    
    ※全て割り切れる問題のみ出題されます  
    ※割り算モードでは問題ごとに制限時間があります
    """)
    
    if st.button("🚀 ゲーム開始", type="primary", use_container_width=True):
        start_game()
        st.rerun()

elif st.session_state.game_state == 'playing':
    # 時間切れチェック（タイムアタックモード）
    if is_time_up():
        st.session_state.game_state = 'result'
        st.rerun()
    
    # 問題ごとの制限時間チェック（割り算モード）
    if is_question_time_up() and not st.session_state.time_limit_exceeded:
        st.session_state.time_limit_exceeded = True
        # 制限時間オーバーとして処理
        is_correct, question_time, time_limit_exceeded = check_answer(-999999)  # ダミーの間違った答え
        st.error("⏰ 制限時間オーバー！")
        time.sleep(1)
        next_question()
        st.rerun()
    
    # プログレスバーまたは時間表示
    if st.session_state.game_mode == 'normal':
        progress = st.session_state.question_count / st.session_state.total_questions
        st.progress(progress)
    else:
        # タイムアタックモードでは残り時間を表示
        remaining_time = get_remaining_time()
        if remaining_time is not None:
            progress = 1 - (remaining_time / st.session_state.time_attack_duration)
            st.progress(progress)
    
    # 問題ごとの制限時間表示（割り算モード）
    question_remaining = get_question_remaining_time()
    if question_remaining is not None:
        if question_remaining <= 3:
            st.error(f"⏰ 残り時間: {question_remaining:.1f}秒 🚨")
        elif question_remaining <= 5:
            st.warning(f"⏰ 残り時間: {question_remaining:.1f}秒")
        else:
            st.info(f"⏰ 制限時間: {question_remaining:.1f}秒")
    
    # メトリクス表示
    if st.session_state.game_mode == 'normal':
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        
        with col1:
            st.metric("問題", f"{st.session_state.question_count + 1}/{st.session_state.total_questions}")
        
        with col2:
            st.metric("正解数", st.session_state.score)
        
        with col3:
            # 連続正解記録を強調表示
            streak_color = "🔥" if st.session_state.current_streak >= 5 else "⭐" if st.session_state.current_streak >= 3 else ""
            st.metric("連続正解", f"{streak_color}{st.session_state.current_streak}")
        
        with col4:
            elapsed_time = time.time() - st.session_state.start_time
            st.metric("経過時間", f"{elapsed_time:.1f}秒")
    else:
        # タイムアタックモード
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        
        with col1:
            remaining_time = get_remaining_time()
            if remaining_time is not None:
                if remaining_time <= 10:
                    st.metric("⏰ 残り時間", f"🚨{remaining_time:.1f}秒")
                else:
                    st.metric("⏰ 残り時間", f"{remaining_time:.1f}秒")
        
        with col2:
            st.metric("解答数", f"{st.session_state.question_count}問")
        
        with col3:
            st.metric("正解数", f"✅{st.session_state.score}")
        
        with col4:
            # 連続正解記録を強調表示
            streak_color = "🔥" if st.session_state.current_streak >= 5 else "⭐" if st.session_state.current_streak >= 3 else ""
            st.metric("連続正解", f"{streak_color}{st.session_state.current_streak}")
    
    st.markdown("---")
    
    # 問題表示
    st.markdown(f"### 問題: {st.session_state.current_question} = ?")
    
    # 回答入力
    with st.form("answer_form"):
        user_answer = st.number_input("答えを入力してください", step=1)
        submitted = st.form_submit_button("回答", type="primary", use_container_width=True)
        
        if submitted:
            is_correct, question_time, time_limit_exceeded = check_answer(int(user_answer))
            
            if time_limit_exceeded:
                st.error(f"⏰ 制限時間オーバー！正解は {st.session_state.current_answer} でした。")
            elif is_correct:
                streak_msg = ""
                if st.session_state.current_streak >= 10:
                    streak_msg = f" 🎉 素晴らしい！{st.session_state.current_streak}連続正解！"
                elif st.session_state.current_streak >= 5:
                    streak_msg = f" 🔥 {st.session_state.current_streak}連続正解中！"
                elif st.session_state.current_streak >= 3:
                    streak_msg = f" ⭐ {st.session_state.current_streak}連続正解！"
                
                st.success(f"✅ 正解！ ({question_time:.2f}秒){streak_msg}")
            else:
                broken_streak_msg = ""
                if st.session_state.current_streak == 0 and len(st.session_state.history) > 1:
                    # 前の問題で連続記録が途切れた場合
                    prev_streak = st.session_state.history[-2].get('streak_at_time', 0) if len(st.session_state.history) >= 2 else 0
                    if prev_streak >= 3:
                        broken_streak_msg = f" ({prev_streak}連続記録が途切れました)"
                
                st.error(f"❌ 不正解。正解は {st.session_state.current_answer} でした。 ({question_time:.2f}秒){broken_streak_msg}")
            
            time.sleep(1)  # 結果を表示する時間
            next_question()
            st.rerun()

elif st.session_state.game_state == 'result':
    # 結果のタイトルをモードに応じて変更
    if st.session_state.game_mode == 'time_attack':
        st.header("⏱️ タイムアタック結果")
    else:
        st.header("🎉 結果発表")
    
    total_time = time.time() - st.session_state.start_time
    
    # タイムアタックモードでは最終的な時間を60秒に固定
    if st.session_state.game_mode == 'time_attack':
        total_time = st.session_state.time_attack_duration
    
    if st.session_state.question_count > 0:
        accuracy = (st.session_state.score / st.session_state.question_count) * 100
        avg_time = sum([h['time'] for h in st.session_state.history]) / len(st.session_state.history)
    else:
        accuracy = 0
        avg_time = 0
    
    # メトリクス表示をモードに応じて変更
    if st.session_state.game_mode == 'time_attack':
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("解答数", f"{st.session_state.question_count}問")
        
        with col2:
            st.metric("正解数", f"{st.session_state.score}問")
        
        with col3:
            st.metric("正答率", f"{accuracy:.1f}%")
        
        with col4:
            st.metric("最高連続正解", f"🏆{st.session_state.max_streak}")
        
        with col5:
            if avg_time > 0:
                questions_per_minute = 60 / avg_time
                st.metric("問/分", f"{questions_per_minute:.1f}")
    else:
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("正解数", f"{st.session_state.score}/{st.session_state.total_questions}")
        
        with col2:
            st.metric("正答率", f"{accuracy:.1f}%")
        
        with col3:
            st.metric("最高連続正解", f"🏆{st.session_state.max_streak}")
        
        with col4:
            st.metric("総時間", f"{total_time:.1f}秒")
        
        with col5:
            st.metric("平均時間", f"{avg_time:.2f}秒/問")
    
    # パフォーマンス評価をモードに応じて変更
    streak_bonus = ""
    if st.session_state.max_streak >= 10:
        streak_bonus = f" 連続正解記録{st.session_state.max_streak}回は素晴らしい！"
    elif st.session_state.max_streak >= 5:
        streak_bonus = f" {st.session_state.max_streak}連続正解、集中力抜群！"
    
    if st.session_state.game_mode == 'time_attack':
        # タイムアタック用の評価
        if st.session_state.question_count >= 30 and accuracy >= 90:
            st.success(f"🏆 スーパーマスター！1分間で{st.session_state.question_count}問も解くなんて凄すぎます！{streak_bonus}")
        elif st.session_state.question_count >= 20 and accuracy >= 80:
            st.info(f"🔥 暗算の達人！1分間で{st.session_state.question_count}問、素晴らしいスピードです！{streak_bonus}")
        elif st.session_state.question_count >= 15:
            st.success(f"👍 とても良いペース！1分間で{st.session_state.question_count}問解けました！{streak_bonus}")
        elif st.session_state.question_count >= 10:
            st.warning(f"📚 もう少し練習すればスピードアップできますよ！{streak_bonus}")
        else:
            st.error(f"💪 タイムアタックは難しいですが、練習すれば必ず上達します！{streak_bonus}")
    else:
        # 通常モード用の評価
        if accuracy >= 90 and avg_time <= 3:
            st.success(f"🏆 素晴らしい！暗算マスターです！{streak_bonus}")
        elif accuracy >= 80 and avg_time <= 5:
            st.info(f"👍 とても良い成績です！{streak_bonus}")
        elif accuracy >= 70:
            st.warning(f"📚 もう少し練習すれば上達しますよ！{streak_bonus}")
        else:
            st.error(f"💪 練習あるのみ！頑張りましょう！{streak_bonus}")
    
    # 全時間記録の表示
    if st.session_state.all_time_best_streak > st.session_state.max_streak:
        st.info(f"🎯 あなたの全時間最高連続正解記録: {st.session_state.all_time_best_streak}回")
    
    st.markdown("---")
    
    # 詳細履歴
    st.subheader("📊 詳細履歴")
    
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        df['結果'] = df.apply(lambda row: '⏰' if row.get('time_limit_exceeded', False) else ('✅' if row['is_correct'] else '❌'), axis=1)
        df['連続記録'] = df['streak_at_time']
        
        # 表示する列を選択
        display_cols = ['question', 'user_answer', 'correct_answer', '結果', 'time', '連続記録']
        col_names = ['問題', 'あなたの答え', '正解', '結果', '時間(秒)', '連続記録']
        
        df_display = df[display_cols].copy()
        df_display.columns = col_names
        
        st.dataframe(df_display, use_container_width=True)
        
        # 統計情報
        st.subheader("📈 統計情報")
        correct_times = [h['time'] for h in st.session_state.history if h['is_correct']]
        incorrect_times = [h['time'] for h in st.session_state.history if not h['is_correct']]
        timeout_count = len([h for h in st.session_state.history if h.get('time_limit_exceeded', False)])
        
        if st.session_state.game_mode == 'time_attack':
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if correct_times:
                    st.metric("正解時の平均時間", f"{sum(correct_times)/len(correct_times):.2f}秒")
            with col2:
                if incorrect_times:
                    st.metric("不正解時")
