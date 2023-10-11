#各種のインポート
import torch
from torch import nn,optim
from torch.utils.data import DataLoader, TensorDataset, Dataset
from torchvision import transforms
from torchinfo import summary #torchinfoはニューラルネットの中身を見れるのでおすすめ
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
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

#データを3行だけ表示
print(df.head(3))

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
print("train size: {}, test size: {} ".format(len(train), len(test)))

time_stemp = 10 #今回は10個のシーケンシャルデータを1固まりとするので10を設定
n_sample = train_size - time_stemp - 1 #学習予測サンプルはt=10~99なので89個

#シーケンシャルデータの固まり数、シーケンシャルデータの長さ、RNN_cellへの入力次元(1次元)に形を成形
input_data = np.zeros((n_sample, time_stemp, 1)) #シーケンシャルデータを格納する箱を用意(入力)
correct_input_data = np.zeros((n_sample, 1)) #シーケンシャルデータを格納する箱を用意(正解)

print(input_data.shape)
print(correct_input_data.shape)


#空のシーケンシャルデータを入れる箱に実際のデータを入れていく
"""
こんなイメージ？
0,1,2,・・・9        +  正解データt=10
  1,2,・・・9,10     +  正解データt=11
    2,・・・9,10,11  +  正解データt=12
"""
for i in range(n_sample):
    input_data[i] = df_scaled[i:i+time_stemp].reshape(-1, 1)
    correct_input_data[i] = df_scaled[i+time_stemp:i+time_stemp+1]

input_data = torch.tensor(input_data, dtype=torch.float) #Tensor化(入力)
correct_data = torch.tensor(correct_input_data, dtype=torch.float) #Tensor化(正解)
dataset = torch.utils.data.TensorDataset(input_data, correct_data) #データセット作成
train_loader = DataLoader(dataset, batch_size=4, shuffle=True) #データローダー作成

class My_rnn_net(nn.Module):
    def __init__(self, input_size, output_size, hidden_dim, n_layers):
        super(My_rnn_net, self).__init__()

        self.input_size = input_size #入力データ(x)
        self.hidden_dim = hidden_dim #隠れ層データ(hidden)
        self.n_layers = n_layers #RNNを「上方向に」何層重ねるか？の設定 ※横方向ではない

        self.rnn = nn.RNN(input_size, hidden_dim, n_layers, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_size) #全結合層でhiddenからの出力を1個にする

    def forward(self, x):
        #h0 = torch.zeros(self.n_layers, x.size(0), self.hidden_dim).to(device)
        #y_rnn, h = self.rnn(x, h0)
        y_rnn, h = self.rnn(x, None) #hidden部分はコメントアウトした↑2行と同じ意味になっている。
        y = self.fc(y_rnn[:, -1, :]) #最後の時刻の出力だけを使用するので「-1」としている

        return y

#RNNの設定
n_inputs  = 1
n_outputs = 1
n_hidden  = 64 #隠れ層(hidden)を64個に設定
n_layers  = 1

net = My_rnn_net(n_inputs, n_outputs, n_hidden, n_layers) #RNNをインスタンス化
print(net) #作成したRNNの層を簡易表示

#おすすめのtorchinfoでさらに見やすく表示
batch_size = 4
summary(net, (batch_size, 10, 1))

loss_fnc = nn.MSELoss() #損失関数はMSE
optimizer = optim.Adam(net.parameters(), lr=0.001) #オプティマイザはAdam
loss_record = [] #lossの推移記録用
device = torch.device("cuda:0" if torch.cuda. is_available() else "cpu")  #デバイス(GPU or CPU)設定 
epochs = 1 #エポック数

net.to(device) #モデルをGPU(CPU)へ

for i in range(epochs+1):
    net.train() #学習モード
    running_loss =0.0 #記録用loss初期化
    for j, (x, t) in enumerate(train_loader): #データローダからバッチ毎に取り出す
        x = x.to(device) #シーケンシャルデータをバッチサイズ分だけGPUへ
        optimizer.zero_grad() #勾配を初期化
        y = net(x) #RNNで予測
        y = y.to('cpu') #予測結果をCPUに戻す
        loss = loss_fnc(y, t) #MSEでloss計算
        loss.backward()  #逆伝番        
        optimizer.step()  #勾配を更新        
        running_loss += loss.item()  #バッチごとのlossを足していく
    running_loss /= j+1 #lossを平均化
    loss_record.append(running_loss) #記録用のlistにlossを加える

    """以下RNNの学習の経過を可視化するコード"""
    if i%10 == 0: #今回は100エポック毎に学習がどう進んだか？を表示させる
        print('Epoch:', i, 'Loss_Train:', running_loss)
        input_train = list(input_data[0].reshape(-1)) #まず最初にt＝0～9をlist化しておく
        predicted_train_plot = [] #学習結果plot用のlist
        net.eval() #予測モード
        for k in range(n_sample): #学習させる点の数だけループ
            x = torch.tensor(input_train[-time_stemp:]) #最新の10個のデータを取り出してTensor化
            x = x.reshape(1, time_stemp, 1) #予測なので当然バッチサイズは1
            x = x.to(device).float() #GPUへ
            y = net(x) #予測
            y = y.to('cpu') #結果をCPUへ戻す
            """
            もっと綺麗なやり方あるかもですが、次のループで値をずらす為の部分。
            t=0～9の予測が終了 ⇒ t=1～10で予測させたいのでt=10を追加する・・・を繰り返す
            """
            if k <= n_sample-2: 
                input_train.append(input_data[k+1][9].item())
            predicted_train_plot.append(y[0].item())

filename = 'finalized_model.sav'
pickle.dump(net, open(filename, 'wb'))

loaded_net = pickle.load(open(filename, 'rb'))

#学習の時と同じ感じでまずは空のデータを作る
time_stemp = 10
n_sample_test = len(df_scaled) - train_size #テストサイズは学習で使ってない部分
test_data = np.zeros((n_sample_test, time_stemp, 1))
correct_test_data = np.zeros((n_sample_test, 1))

#t=90以降のデータを抜粋してシーケンシャルデータとして格納していく
start_test = 1350
for i in range(n_sample_test):
    test_data[i] = df_scaled[start_test+i : start_test+i+time_stemp].reshape(-1, 1)
    correct_test_data[i] = df_scaled[start_test+i+time_stemp : start_test+i+time_stemp+1]

#以下は学習と同じ要領
input_test = list(test_data[0].reshape(-1))
predicted_test_plot = []
loaded_net.eval()
for k in range(n_sample_test):
    x = torch.tensor(input_test[-time_stemp:])
    x = x.reshape(1, time_stemp, 1)
    x = x.to(device).float()
    y = loaded_net(x)
    y = y.to('cpu')
    if k <= n_sample_test-2: 
        input_test.append(test_data[k+1][9].item())
    predicted_test_plot.append(y[0].item())

plt.plot(range(len(df_scaled)), df_scaled, label='Correct')
plt.plot(range(time_stemp, time_stemp+len(predicted_train_plot)), predicted_train_plot, label='Predicted')
plt.legend()
plt.show()

#最後にlossの推移を確認
plt.plot(range(len(loss_record)), loss_record, label='train')
plt.legend()

plt.xlabel("epochs")
plt.ylabel("loss")
plt.show()

plt.plot(range(len(df_scaled)), df_scaled, label='Correct')
plt.plot(range(start_test+time_stemp, start_test+time_stemp+len(predicted_test_plot)), predicted_test_plot , label='Predicted')
plt.legend()
plt.show()
