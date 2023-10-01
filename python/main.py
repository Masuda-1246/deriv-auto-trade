import asyncio
import pprint
from deriv_api import DerivAPI
from rx import Observable
from datetime import datetime

import app.models
from app.models.base import Tick

app_id = 1089

async def sample_calls():
    api = DerivAPI(app_id=app_id)
    # R_50のtickを購読し、新しいtickが到着するたびにコールバック関数を呼び出すObservableを作成します
    source_tick_50: Observable  = await api.subscribe({'ticks': '1HZ50V'})

    def create_subs_cb(data):
        # print(f"Received new tick data for R_50: {data}")
        now = datetime.now()
        tick = Tick.create(now, data['tick']['ask'], data['tick']['bid'])
        print(f"Received new tick data for 1HZ50V: {tick.timestamp}, {tick.price}")
        # print(f"Received new tick data for 1HZ50V: {tick.timestamp}, {tick.price}, {round(pre_tick.price-tick.price)}")

    source_tick_50.subscribe(create_subs_cb)
    # 無限ループを実行して、新しいtickを待ち続けます
    while True:
        await asyncio.sleep(1)  # 1秒ごとに新しいtickを待つ（適宜調整可能）

async def sample_calls2():
    api = DerivAPI(app_id=app_id)
    # R_50のtickを購読し、新しいtickが到着するたびにコールバック関数を呼び出すObservableを作成します
    source_tick_50: Observable  = await api.subscribe({'ticks': '1HZ50V'})

    def create_subs_cb(data):
        # print(f"Received new tick data for R_50: {data}")
        now = datetime.now()
        tick = Tick.create(now, data['tick']['ask'], data['tick']['bid'])
        print(f"Received new tick data for 1HZ50V: {tick.timestamp}, {tick.price}")
        # print(f"Received new tick data for 1HZ50V: {tick.timestamp}, {tick.price}, {round(pre_tick.price-tick.price)}")

    source_tick_50.subscribe(create_subs_cb)
    # 無限ループを実行して、新しいtickを待ち続けます
    while True:
        print("Waiting for new ticks...2")
        await asyncio.sleep(1)  # 1秒ごとに新しいtickを待つ（適宜調整可能）

asyncio.run(sample_calls())


