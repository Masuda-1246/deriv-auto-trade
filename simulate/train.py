from stable_baselines3 import PPO
from environment import PricePredictionEnv

# カスタム環境を作成
env = PricePredictionEnv(data_path="sample_writer_row.csv")

# 強化学習エージェントを選択（PPOを使用）
model = PPO("MlpPolicy", env, verbose=1)

# 学習
model.learn(total_timesteps=10000)

# 学習済みモデルを保存
model.save("price_prediction_model")
