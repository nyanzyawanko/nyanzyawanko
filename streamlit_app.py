import random
import time

# 関数：暗算問題を出題
def math_practice():
    # ランダムに問題の種類を選択（加算、引き算、掛け算、割り算）
    operation = random.choice(['+', '-', '*', '/'])

    if operation == '+':
        num1 = random.randint(1, 9)
        num2 = random.randint(1, 9)
        question = f"{num1} + {num2} = ?"
        correct_answer = num1 + num2

    elif operation == '-':
        num1 = random.randint(1, 9)
        num2 = random.randint(1, num1)  # 引き算なので、num2 <= num1に設定
        question = f"{num1} - {num2} = ?"
        correct_answer = num1 - num2

    elif operation == '*':
        num1 = random.randint(1, 9)
        num2 = random.randint(1, 9)
        question = f"{num1} * {num2} = ?"
        correct_answer = num1 * num2

    elif operation == '/':
        num2 = random.randint(1, 9)
        correct_answer = random.randint(1, 9)
        num1 = correct_answer * num2  # 割り算のため、num1 は num2 と正確に割り切れるように設定
        question = f"{num1} / {num2} = ?"

    print("問題:", question)

    # タイマー開始
    start_time = time.time()

    # ユーザーに解答を求める
    answer = float(input("答えを入力してください: "))  # 小数にも対応

    # タイマー終了
    end_time = time.time()

    # 正誤判定
    if answer == correct_answer:
        print("正解！")
    else:
        print(f"不正解... 正解は {correct_answer} です。")
    
    # 経過時間表示
    elapsed_time = end_time - start_time
    print(f"解答にかかった時間: {elapsed_time:.2f} 秒")

# 練習の繰り返し
def main():
    while True:
        math_practice()
        again = input("もう一度練習しますか？ (y/n): ").strip().lower()
        if again != 'y':
            print("練習を終了します。お疲れ様でした！")
            break

if __name__ == "__main__":
    main()
