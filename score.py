def num():
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
    pages = ["/cart", "/info", "/shop","/my-account","/checkout"]

    # 項目ファイルを読み込んで条件に合う項目を取得
    item_path = "tank_status.csv"  # 項目ファイルのパス
    if not os.path.isfile(item_path):

        # 項目データを定義
        data = {
            "Path": pages,
            "Value": [0 for _ in range(len(pages))]  # サンプルデータとして、適当に値を割り振る
        }

        # DataFrameを作成
        item_status_df = pd.DataFrame(data)

        # CSVファイルに保存
        file_path = "tank_status.csv"
        item_status_df.to_csv(file_path, index=False)

    item_df = pd.read_csv(item_path)

    # 値が0の項目だけを抽出
    valid_pages = item_df[item_df["Value"] == 0]["Path"].tolist()
    final_lst = ["cart", "info", "pay", "account", "items"]

    if is_file and valid_pages != []:
        df = pd.read_csv(path)  # データ読み込み

        try_num = df.groupby("Path").count().loc["/cart", "Timestamp"]  # 計測回数
        alpha = np.log(7 / 3) / (try_num - 1)  # 一番過去(重み)/現在(重み)=7/3となるように設定
        w = np.array([np.e ** (-1 * (try_num - 1 - i) * alpha) for i in range(try_num)])  # 重みを計算

        for page in valid_pages:
            np_lst = np.array(df[df.loc[:, "Path"] == page].loc[:, "Access Count"])
            total = np.sum(np_lst * w)
            scores.append(total)
        scores = np.array(scores)

    elif valid_pages == []:
        return {key: 0 for key in final_lst}

    else:
        df = pd.read_csv("access_counts_past.csv")
        for page in valid_pages:
            scores.append(int(df[df.loc[:, "Path"] == page].loc[:, "Access Count"].iloc[0]))

    # スコアの正規化（Zスコア正規化）
    if len(valid_pages) == 1:
        probabilities = [1]
    else:
        mean_score = np.mean(scores)
        std_score = np.std(scores)
        normalized_scores = (scores - mean_score) / std_score  # 平均0、標準偏差1に正規化
        # 確率を計算
        probabilities = softmax(normalized_scores)
    dct = {}

    for page, pro in zip(valid_pages, probabilities):
        if page == "/cart":
            page = "cart"
        elif page == "/info":
            page = "info"
        if page == "/checkout":
            page = "pay"
        if page == "/my-account":
            page = "account"
        if page == "/shop":
            page = "items"
        dct[page] = pro

    for item in final_lst:
        if item not in dct:
            dct[item] = 0
    # 結果を表示
    return dct