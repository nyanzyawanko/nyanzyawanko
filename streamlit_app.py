import streamlit as st
import random
from datetime import datetime

st.title("🔮 今日の運勢占いアプリ")

# ユーザー情報の入力
name = st.text_input("あなたの名前を入力してください")
birthdate = st.date_input("あなたの誕生日を選んでください")

# 占い結果の候補
fortunes = [
    "大吉 🌟：今日は素晴らしい一日になります！",
    "中吉 😊：まあまあいい日になりそうです。",
    "小吉 🙂：小さなラッキーがあるかも。",
    "吉 😌：普通の日。でも何かに感謝できそう。",
    "凶 😥：ちょっと注意が必要な日です。慎重に行動しましょう。",
    "大凶 💀：今日は無理をせず、静かに過ごすのが吉。"
]

# 占うボタン
if st.button("占う！"):
    if name:
        seed = int(datetime.now().strftime("%Y%m%d")) + sum(ord(c) for c in name)
        random.seed(seed)
        result = random.choice(fortunes)
        st.subheader(f"{name}さんの今日の運勢は…")
        st.success(result)
    else:
        st.warning("名前を入力してください！")
