import gym
from gym import spaces
import pandas as pd
import numpy as np
from datetime import datetime

class PricePredictionEnv(gym.Env):
    def __init__(self, data_path):
        super(PricePredictionEnv, self).__init__()

        # データ読み込み
        self.data = pd.read_csv(data_path)
        self.current_step = 0
        self.target_price = 150

        self.action_memory = []
        self.price_memory = []

        # 行動スペースを定義（0: 達するに賭ける、1: 達さないに賭ける、2: 賭けない）
        self.action_space = spaces.Discrete(3)

        # 観測スペースを定義
        self.observation_space = spaces.Box(low=-float('inf'), high=float('inf'), shape=(2,), dtype=np.float32)

    def reset(self):
        # 初期化
        self.current_step = 0
        self.current_price = self.data.iloc[self.current_step]['price']
        self.current_timestamp = self.data.iloc[self.current_step]['timestamp']
        self.action_memory = []
        self.price_memory = []
        return np.array([self.current_price, self._convert_timestamp(self.current_timestamp)])

    def step(self, action):
        # 行動の実行
        assert self.action_space.contains(action)

        # 新しい価格を計算
        self.current_step += 1
        self.action_memory.append(action)
        self.price_memory.append(self.current_price)
        reward = 0
        if len(self.action_memory) == 120:
            reward_price = self.price_memory.pop(0)
            self.action_memory.pop(0)
            reward_action = self.action_memory[0]
            max_price = max(self.price_memory)
            if reward_action == 0:
                if max_price >= reward_price + self.target_price:
                    reward = 2
                else:
                    reward = -7
            elif reward_action == 1:
                if max_price < reward_price + self.target_price:
                    reward = 5
                else:
                    reward = -30
            elif reward_action == 2:
                reward = 0.5

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
