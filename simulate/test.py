import asyncio
import time
import numpy as np
from datetime import datetime
from stable_baselines3 import PPO
import requests



async def main():
    # 学習済みモデルを読み込む
    model_path = "./price_prediction_model.zip"
    loaded_model = PPO.load(model_path)

    # リアルタイムデータの取得と取引
    while True:
        # 現在価格を取得
        current_price = await get_price()

        # 現在タイムスタンプを取得
        current_timestamp = datetime.now().timestamp()

        # 現在価格とタイムスタンプを観測値に変換
        observation = np.array([current_price, current_timestamp])

        # 学習済みモデルを使用してアクションを選択
        action, _ = loaded_model.predict(observation)

        # 選択したアクションに基づいて取引を実行
        if action == 0:  # 達するに賭ける
            price = await buy_touch()
            print(f"buy touch {price}")
        elif action == 1:  # 達さないに賭ける
            # price = await buy_no_touch()
            print(f"buy no touch")
        else:
            print("do nothing")
        time.sleep(1)
        # ゲーム状態の更新などが必要な場合は追加してください


async def get_price():
    # http://127.0.0.0:8080/api/tickにアクセスし、最新の価格を取得
    # url = "http://127.0.0.1:8080/api/tick/"
    url = "http://localhost:22000/price"
    r = requests.get(url)
    return float(r.json()['price'])

async def buy_touch():
    url = "http://localhost:22000/touch"
    r = requests.post(url)
    return r.json()['price']

async def buy_no_touch():
    url = "http://localhost:22000/notouch"
    r = requests.post(url)
    return r.json()['price']


asyncio.run(main())