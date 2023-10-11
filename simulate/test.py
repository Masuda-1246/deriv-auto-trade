import asyncio
import time
import numpy as np
from datetime import datetime
from stable_baselines3 import PPO
import requests
import math
from app.models.base import Tick



async def main():
    # 学習済みモデルを読み込む
    model_path = "./price_prediction_model.zip"
    loaded_model = PPO.load(model_path)
    pre_result = 1696406582
    # リアルタイムデータの取得と取引
    time_sleep = 0
    refresh_sleep = 0
    count = 0
    while True:
        try:
            # 現在価格を取得
            current_price = await get_price()
            if current_price == 0:
                raise Exception("price is 0")

            # 現在タイムスタンプを取得
            now = datetime.now()
            current_timestamp = now.timestamp()
            Tick.create(now, current_price, current_price)
            count += 1
            print(f"{round(current_timestamp)} {current_price} : {count}")
            # time.sleep(1)
            # continue

            # 現在価格とタイムスタンプを観測値に変換
            observation = np.array([current_price, current_timestamp])
            result = math.floor(current_timestamp / 200) * 200
            if pre_result != result:
                await save_model(loaded_model)
                pre_result = result
                refresh_sleep += 1
                if refresh_sleep == 10:
                    r = await refresh()
                    print(r)
                    refresh_sleep = 0
            # 学習済みモデルを使用してアクションを選択
            action, _ = loaded_model.predict(observation)

            if time_sleep == 0:
                if action == 0:  # 達するに賭ける
                    await buy_touch()
                    print(f"{round(current_timestamp)} buy touch")
                elif action == 1:  # 達さないに賭ける
                    # await buy_no_touch()
                    print(f"{round(current_timestamp)} buy no touch")
                else:
                    print(f"{round(current_timestamp)} do nothing")
            else:
                print(f"{round(current_timestamp)} do nothing")

            time_sleep += 1
            time_sleep %= 3
            time.sleep(1)
        except Exception as e:
            print(e)
            r = await refresh()
            print(r)
            continue

async def get_price():
    # url = "http://127.0.0.1:8080/api/tick/"
    url = "http://localhost:22000/price"
    r = requests.get(url)
    return float(r.json()['price'])

async def get_balance():
    # url = "http://127.0.0.1:8080/api/tick/"
    # url = "http://127.0.0.1:8080/api/tick/"
    url = "http://localhost:22000/balance"
    r = requests.get(url)
    return r.json()['balance']

def get_rate():
    url = "http://127.0.0.1:8080/api/rate"
    requests.get(url)
    print("get rate success")

async def buy_touch():
    url = "http://localhost:22000/touch"
    r = requests.post(url)
    return r.json()['price']

async def buy_no_touch():
    url = "http://localhost:22000/notouch"
    r = requests.post(url)
    return r.json()['price']

async def save_model(model):
    print("save model")
    model.save("./price_prediction_model.zip")
    await screanshot()

async def screanshot():
    url = "http://localhost:22000/screenshot"
    r = requests.post(url)

async def refresh():
    url = "http://localhost:22000/refresh"
    r = requests.post(url)
    return r

asyncio.run(main())