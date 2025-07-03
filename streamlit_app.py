import streamlit as st
import random
import time

# 時間制限マップ
TIME_LIMITS = {1: 5, 2: 10, 3: 20}

# 問題生成関数
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

# Streamlit UI
def main():
    st.title("⏱️ 高速暗算トレーニング")
    st.write("掛け算・割り算に挑戦！制限時間内に答えてください。")

    level = st.selectbox("難易度を選択", [1, 2, 3], format_func=lambda x: {
        1: "レベル1（1桁 × 1桁 / ÷）",
        2: "レベル2（2桁 × 1桁 / ÷）",
        3: "レベル3（2桁 × 2桁 / 3桁 ÷ 2桁）"
    }[x])

    if "question_num" not in st.session_state:
        st.session_state.question_num = 1
        st.session_state.score = 0
        st.session_state.start_time = None
        st.session_state.question, st.session_state.answer = generate_problem(level)

    time_limit = TIME_LIMITS[level]

    st.subheader(f"問題 {st.session_state.question_num}")
    st.markdown(f"**{st.session_state.question} = ?**")
    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()

    user_input = st.text_input("答えを入力してEnter")

    elapsed = time.time() - st.session_state.start_time

    if user_input:
        try:
            user_answer = int(user_input)
            if elapsed > time_limit:
                st.error("時間切れ！")
                st.info(f"正解は {st.session_state.answer} でした。")
            elif user_answer == st.session_state.answer:
                st.success("正解！")
                st.session_state.score += 1
            else:
                st.error("不正解")
                st.info(f"正解は {st.session_state.answer} でした。")
        except:
            st.warning("数値で入力してください。")

        # 次の問題へ
        st.session_state.question_num += 1
        st.session_state.start_time = None
        st.session_state.question, st.session_state.answer = generate_problem(level)
        st.experimental_rerun()

    st.write(f"現在のスコア: {st.session_state.score} / {st.session_state.question_num - 1}")

    if st.button("リセット"):
        st.session_state.question_num = 1
        st.session_state.score = 0
        st.session_state.start_time = None
        st.session_state.question, st.session_state.answer = generate_problem(level)
        st.experimental_rerun()

if __name__ == "__main__":
    main()
