#各種のインポート
import torch
from torch import nn,optim
from torch.utils.data import DataLoader, TensorDataset, Dataset
from torchvision import transforms
from torchinfo import summary #torchinfoはニューラルネットの中身を見れるのでおすすめ
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import pickle
import pandas as pd
import os
import random



#乱数固定用の処理
seed = 10
torch.manual_seed(seed)
torch.cuda.manual_seed(seed)

#データをPandasで読み込み
df = pd.read_csv("sample_writer_row.csv")

#Monthカラムは解析に不要なので排除
df = df.iloc[:,1].values
#乗客数の1次元データとする
df = df.reshape(-1,1)
df = df.astype("float32")


#ニューラルネットの入力データは0～1へ正規化する必要があるので乗客数を正規化する
scaler = MinMaxScaler(feature_range = (0, 1))
df_scaled = scaler.fit_transform(df)

train_size = int(len(df_scaled) * 0.70) #学習サイズ(100個)
test_size = len(df_scaled) - train_size #全データから学習サイズを引けばテストサイズになる
train = df_scaled[0:train_size,:] #全データから学習の個所を抜粋
test = df_scaled[train_size:len(df_scaled),:] #全データからテストの個所を抜粋


class My_rnn_net(nn.Module):
    def __init__(self, input_size, output_size, hidden_dim, n_layers):
        super(My_rnn_net, self).__init__()

        self.input_size = input_size #入力データ(x)
        self.hidden_dim = hidden_dim #隠れ層データ(hidden)
        self.n_layers = n_layers #RNNを「上方向に」何層重ねるか？の設定 ※横方向ではない

        self.rnn = nn.RNN(input_size, hidden_dim, n_layers, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_size) #全結合層でhiddenからの出力を1個にする

    def forward(self, x):
        y_rnn, h = self.rnn(x, None) #hidden部分はコメントアウトした↑2行と同じ意味になっている。
        y = self.fc(y_rnn[:, -1, :]) #最後の時刻の出力だけを使用するので「-1」としている

        return y

device = torch.device("cuda:0" if torch.cuda. is_available() else "cpu")  #デバイス(GPU or CPU)設定 

filename = 'finalized_model.sav'

loaded_net = pickle.load(open(filename, 'rb'))

#学習の時と同じ感じでまずは空のデータを作る
time_stemp = 10
n_sample_test = len(df_scaled) - train_size #テストサイズは学習で使ってない部分
test_data = np.zeros((n_sample_test, time_stemp, 1))
correct_test_data = np.zeros((n_sample_test, 1))

#t=90以降のデータを抜粋してシーケンシャルデータとして格納していく
start_test = 13990
for i in range(n_sample_test):
    test_data[i] = df_scaled[start_test+i : start_test+i+time_stemp].reshape(-1, 1)

#以下は学習と同じ要領
input_test = list(test_data[0].reshape(-1))
predicted_test_plot = []
loaded_net.eval()
for k in range(n_sample_test-2):
    x = torch.tensor(input_test[-time_stemp:])
    x = x.reshape(1, time_stemp, 1)
    x = x.to(device).float()
    y = loaded_net(x)
    y = y.to('cpu')
    if k <= n_sample_test-2: 
        input_test.append(test_data[k+1][9].item())
    predicted_test_plot.append(y[0].item())

predicted_test_plot = scaler.inverse_transform([predicted_test_plot])
predicted_test_plot = predicted_test_plot[0]
df_plot = scaler.inverse_transform(df_scaled)
plt.plot(range(len(df_plot)), df_plot, label='Correct')
plt.plot(range(start_test+time_stemp, start_test+time_stemp+len(predicted_test_plot)), predicted_test_plot , label='Predicted')
plt.legend()
plt.show()
