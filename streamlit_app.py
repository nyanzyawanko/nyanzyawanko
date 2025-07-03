import streamlit as st
import random
import time

# 時間制限マップ
TIME_LIMITS = {1: 5, 2: 10, 3: 20}

# 問題生成
def generate_problem(level):
    if level == 1:
        a = random.randint(1, 9)
        b = random.randint(1, 9)
        op = random.choice(['*', '/'])
        if op == '*':
            question = f"{a} × {b}"
            answer = a * b
        else:
            answer = a
            dividend = a * b
            question = f"{dividend} ÷ {b}"

    elif level == 2:
        a = random.randint(10, 99)
        b = random.randint(1, 9)
        op = random.choice(['*', '/'])
        if op == '*':
            question = f"{a} × {b}"
            answer = a * b
        else:
            answer = a
            dividend = a * b
            question = f"{dividend} ÷ {b}"

    elif level == 3:
        op = random.choice(['*', '/'])
        if op == '*':
            a = random.randint(10, 99)
            b = random.randint(10, 99)
            question = f"{a} × {b}"
            answer = a * b
        else:
            b = random.randint(10, 99)
            a = random.randint(100, 999) // b
            dividend = a * b
            question = f"{dividend} ÷ {b}"
            answer = a

    return question, answer

# Streamlit アプリ本体
def main():
    st.set_page_config(page_title="高速暗算トレーニング", layout="centered")
    st.title("🧠 高速暗算トレーニング")
    st.write("掛け算・割り算にチャレンジ！各問題には制限時間があります。")

    level = st.selectbox("難易度を選択", [1, 2, 3], format_func=lambda x: {
        1: "レベル1（1桁×1桁 / ÷）",
        2: "レベル2（2桁×1桁 / ÷）",
        3: "レベル3（2桁×2桁 / 3桁÷2桁）"
    }[x])

    time_limit = TIME_LIMITS[level]

    if "question_num" not in st.session_state:
        st.session_state.question_num = 1
        st.session_state.score = 0
        st.session_state.start_time = None
        st.session_state.question, st.session_state.answer = generate_problem(level)
        st.session_state.last_input = ""
        st.session_state.status = ""
        st.session_state.answered = False

    st.subheader(f"問題 {st.session_state.question_num}")
    st.markdown(f"**{st.session_state.question} = ?**")

    timer_placeholder = st.empty()
    input_placeholder = st.empty()

    # タイマー初期化
    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()

    elapsed = time.time() - st.session_state.start_time
    remaining = int(time_limit - elapsed)

    if remaining > 0 and not st.session_state.answered:
        with timer_placeholder.container():
            st.warning(f"⏳ 残り時間: {remaining} 秒")
            time.sleep(1)
            st.experimental_rerun()
    elif not st.session_state.answered:
        st.session_state.status = f"時間切れ！正解は {st.session_state.answer} でした。"
        st.session_state.answered = True

    # 入力フォーム（時間内または終了後も表示）
    if not st.session_state.answered:
        user_input = input_placeholder.text_input("答えを入力してEnter", key=st.session_state.question_num)
        if user_input:
            try:
                user_answer = int(user_input)
                if user_answer == st.session_state.answer:
                    st.session_state.score += 1
                    st.session_state.status = "✅ 正解！"
                else:
                    st.session_state.status = f"❌ 不正解。正解は {st.session_state.answer} でした。"
            except:
                st.session_state.status = "⚠️ 数字で入力してください。"
            st.session_state.answered = True

    # 結果表示
    if st.session_state.answered:
        st.info(st.session_state.status)
        if st.button("次の問題 ▶️"):
            st.session_state.question_num += 1
            st.session_state.start_time = None
            st.session_state.question, st.session_state.answer = generate_problem(level)
            st.session_state.answered = False
            st.experimental_rerun()

    st.markdown("---")
    st.write(f"現在のスコア: **{st.session_state.score} / {st.session_state.question_num - 1 if st.session_state.question_num > 1 else 0}**")

    if st.button("🔁 リセット"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.experimental_rerun()

if __name__ == "__main__":
    main()
