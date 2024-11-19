from flask import Flask, render_template
from get_elements import get_all_elmes

app = Flask(__name__, static_folder='./templates/images')

@app.route('/')
def index():
    # 最初に表示する際にはリストを渡さない（空リストを渡すなど）
    return render_template('index.html')

# データ移行処理をシミュレート
from flask import jsonify
@app.route('/migrate', methods=['POST'])
def migrate():
    # サンプルデータを返す（本来は移行データをここで準備する）
    all_elmes_lst = get_all_elmes()  # list
    return jsonify(all_elmes_lst)  # JSON形式でデータを返す


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)