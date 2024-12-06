import time
from flask import Flask, render_template, jsonify
from get_elements import get_all_elmes
import score
import count_access
import threading
import pandas as pd

app = Flask(__name__, static_folder='./templates/images')

# all_elmes_lstは最初に一度だけ取得して保持
all_elmes_lst = get_all_elmes()

# 最新の Scores を保持する変数
Scores = score.num()

# スコア更新用のロック
lock = threading.Lock()

score_update_thread = None

# スコアを定期的に更新するスレッド
def update_scores():
    while True:
        count_access.write()  # count_accessのwrite処理を呼び出し

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/migrate', methods=['POST'])
def migrate():
    global score_update_thread
    # 最初にall_elmes_lstを返すが、Scoresは時間差で更新される
    all_elmes = all_elmes_lst  # 既に取得したall_elmes_lstを使用

    #スコア更新スレッドがまだ開始されていなければ、開始する
    if score_update_thread is None or not score_update_thread.is_alive():
        update_thread = threading.Thread(target=update_scores, daemon=True)
        update_thread.start()
        print("Score update thread started")

    # 初期状態のScoresを取得
    with lock:
        initial_Scores = Scores

    # 非同期でスコアを更新
    # update_scores関数はバックグラウンドスレッドで動作しているので
    # メインスレッドは最初のレスポンスを即座に返します

    return jsonify({
        'all_elmes': all_elmes,
        'Scores': initial_Scores
    })

@app.route("/get_scores", methods=["GET"])
def get_scores():
    global Scores
    new_scores = score.num()  # Scoresを更新
    with lock:
        Scores = new_scores
    print("Updated Scores:", Scores)
    return jsonify({
        "Scores": Scores
    })

@app.route('/account_trigger', methods=['POST'])
def account_trigger():
    global Scores
    # 必要な処理をここに記述
    print("account is triggered!")
    df=pd.read_csv("tank_status.csv")
    df.loc[df['Path'] == '/my-account', 'Value'] = 1
    print(df)
    file_path = "tank_status.csv"
    df.to_csv(file_path, index=False)
    new_scores = score.num()  # Scoresを更新
    with lock:
        Scores = new_scores
    print(Scores)
    return jsonify({"Scores": Scores})

@app.route('/checkout_trigger', methods=['POST'])
def checkout_trigger():
    global Scores
    # 必要な処理をここに記述
    print("checkout is triggered!")
    df=pd.read_csv("tank_status.csv")
    df.loc[df['Path'] == '/checkout', 'Value'] = 1
    print(df)
    file_path = "tank_status.csv"
    df.to_csv(file_path, index=False)
    new_scores = score.num()  # Scoresを更新
    with lock:
        Scores = new_scores
    print(Scores)
    return jsonify({"Scores": Scores})

@app.route('/shop_trigger', methods=['POST'])
def shop_trigger():
    global Scores
    # 必要な処理をここに記述
    print("shop is triggered!")
    df=pd.read_csv("tank_status.csv")
    df.loc[df['Path'] == '/shop', 'Value'] = 1
    print(df)
    file_path = "tank_status.csv"
    df.to_csv(file_path, index=False)
    new_scores = score.num()  # Scoresを更新
    with lock:
        Scores = new_scores
    print(Scores)
    return jsonify({"Scores": Scores})

@app.route('/info_trigger', methods=['POST'])
def info_trigger():
    global Scores
    # 必要な処理をここに記述
    print("info is triggered!")
    df=pd.read_csv("tank_status.csv")
    df.loc[df['Path'] == '/info', 'Value'] = 1
    print(df)
    file_path = "tank_status.csv"
    df.to_csv(file_path, index=False)
    new_scores = score.num()  # Scoresを更新
    with lock:
        Scores = new_scores
    print(Scores)
    return jsonify({"Scores": Scores})

@app.route('/cart_trigger', methods=['POST'])
def cart_trigger():
    global Scores
    # 必要な処理をここに記述
    print("cart is triggered!")
    df=pd.read_csv("tank_status.csv")
    df.loc[df['Path'] == '/cart', 'Value'] = 1
    print(df)
    file_path = "tank_status.csv"
    df.to_csv(file_path, index=False)
    new_scores = score.num()  # Scoresを更新
    with lock:
        Scores = new_scores
    print(Scores)
    return jsonify({"Scores": Scores})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
