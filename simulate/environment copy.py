import gym
from gym import spaces
import pandas as pd
import numpy as np
from datetime import datetime

class PricePredictionEnv2(gym.Env):
    def __init__(self, data_path):
        super(PricePredictionEnv2, self).__init__()

        # データ読み込み
        self.data = pd.read_csv(data_path)
        self.current_step = 0
        
        self.target_price = 150

        # 行動スペースを定義（0: 達するに賭ける、1: 達さないに賭ける、2: 賭けない）
        self.action_space = spaces.Discrete(3)

        # 観測スペースを定義
        self.observation_space = spaces.Box(low=-float('inf'), high=float('inf'), shape=(2,), dtype=np.float32)

    def reset(self):
        # 初期化
        self.current_step = 0
        self.current_price = self.data.iloc[self.current_step]['price']
        self.current_timestamp = self.data.iloc[self.current_step]['timestamp']
        return np.array([self.current_price, self._convert_timestamp(self.current_timestamp)])

    def step(self, action):
        # 行動の実行
        assert self.action_space.contains(action)

        # 価格の変動をシミュレート
        price_change = np.random.uniform(-1.0, 1.0)  # 価格の変動（仮の実装）

        # 新しい価格を計算
        self.current_price += price_change
        self.current_step += 1

        # 報酬の計算
        reward = 0
        if action == 0:  # 達するに賭ける
            if self.current_price >= self.current_price + self.target_price:
                reward = 2
            else:
                reward = -7
        elif action == 1:  # 達さないに賭ける
            if self.current_price < self.current_price + self.target_price:
                reward = 3
            else:
                reward = -25
        elif action == 2:  # 賭けない
            reward = 0.3

        # ゲーム終了の条件を判定
        done = self.current_step >= len(self.data) - 1

        # 新しい観測値を返す
        if not done:
            self.current_timestamp = self.data.iloc[self.current_step]['timestamp']
            new_observation = np.array([self.current_price, self._convert_timestamp(self.current_timestamp)])
        else:
            new_observation = np.array([self.current_price, -1.0])  # ゲーム終了時はタイムスタンプ未知

        return new_observation, reward, done, {}

    def _convert_timestamp(self, timestamp):
        # タイムスタンプを浮動小数点数に変換
        datetime_obj = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
        return datetime_obj.timestamp()
