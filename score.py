import pandas as pd
import numpy as np
import os

scores = []

# ソフトマックス関数
def softmax(x):
    exp_x = np.exp(x - np.max(x))  # オーバーフロー対策で x の最大値を引く
    return exp_x / np.sum(exp_x)

path = "access_counts.csv"
is_file = os.path.isfile(path)
pages = ["/cart", "/sample-page", "/shop","/my-account","/checkout"]

if is_file:
    df = pd.read_csv(path)   #データ読み込み

    try_num = df.groupby("Path").count().loc["/cart", "Timestamp"]  #計測回数
    alpha = np.log(7/3) / (try_num-1)   #一番過去(重み)/現在(重み)=7/3となるように設定
    w = np.array([np.e**(-1*(try_num-1-i)*alpha) for i in range(try_num)])  #重みを計算

    for page in pages:
        np_lst = np.array(df[df.loc[:,"Path"]==page].loc[:,"Access Count"])
        print(np_lst)
        total = np.sum(np_lst*w)
        print(total)
        scores.append(total)
    scores = np.array(scores)

else:
    df = pd.read_csv("access_counts_past.csv")
    for page in pages:
        scores.append(int(df[df.loc[:,"Path"]==page].loc[:,"Access Count"].iloc[0]))    
    
dct = {}
# 確率を計算
probabilities = softmax(scores)
for page, pro in zip(pages, probabilities):
    dct[page] = pro
# 結果を表示
print("スコア:", scores)
print("ソフトマックスで得られる確率:", dct)
print(softmax(np.array([1010, 1000, 900])))