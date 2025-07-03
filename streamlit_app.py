import random
import threading

user_answer = None

def timed_input(prompt, timeout):
    def get_input():
        global user_answer
        user_answer = input(prompt)

    global user_answer
    user_answer = None
    thread = threading.Thread(target=get_input)
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        print("\n時間切れ！")
        return None
    return user_answer

def generate_mul_div_problem(level):
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
            # 2桁 × 2桁
            a = random.randint(10, 99)
            b = random.randint(10, 99)
            question = f"{a} × {b}"
            answer = a * b
        else:
            # 3桁 ÷ 2桁（割り切れるように生成）
            b = random.randint(10, 99)
            a = random.randint(100, 999) // b
            dividend = a * b
            question = f"{dividend} ÷ {b}"
            answer = a
    else:
        raise ValueError("レベルは1〜3のみ対応")

    return question, answer

def get_time_limit(level):
    return {1: 5, 2: 10, 3: 20}.get(level, 10)

def mental_math_trainer(num_questions=5, level=1):
    time_limit = get_time_limit(level)
    print(f"\n📘 レベル {level}｜1問{time_limit}秒以内に回答してください（全{num_questions}問）")
    score = 0

    for i in range(num_questions):
        q, ans = generate_mul_div_problem(level)
        print(f"\n問題 {i+1}: {q} = ?")

        response = timed_input("答え: ", timeout=time_limit)

        if response is None:
            print(f"→ 時間切れ。不正解。正解は {ans} です。")
        else:
            try:
                if int(response) == ans:
                    print("→ 正解！")
                    score += 1
                else:
                    print(f"→ 不正解。正解は {ans} です。")
            except:
                print(f"→ 無効な入力。正解は {ans} です。")

    print(f"\n✅ 結果: {score}/{num_questions} 正解")

def select_difficulty():
    print("🧠 難易度を選んでください：")
    print("1: 九九（1桁×1桁、÷1桁）【5秒】")
    print("2: 中級（2桁×1桁、÷1桁）【10秒】")
    print("3: 上級（2桁×2桁 または 3桁÷2桁）【20秒】")
    while True:
        try:
            level = int(input("レベルを入力（1～3）: "))
            if level in [1, 2, 3]:
                return level
        except:
            pass
        print("無効な入力です。1〜3を選んでください。")

# 実行
if __name__ == "__main__":
    level = select_difficulty()
    mental_math_trainer(num_questions=5, level=level)
