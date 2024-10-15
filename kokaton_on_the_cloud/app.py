from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
import subprocess

app = Flask(__name__)

# 新サーバのデータベース設定
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new_server.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 旧サーバのデータベース設定
old_db_engine = create_engine('sqlite:///old_server.db')  # SQLAlchemyモジュールのcreate_engineを使用

# 新サーバのテーブル定義
class NewTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(250), nullable=True)
    complete = db.Column(db.Boolean, default=False)

# /var/www/htmlの転送元と転送先の情報
sending_directory = # /var/www/html/
recipiment_user = # 転送先ユーザ
recipiment_IP = # 転送先IP
recipiment_directory = #転送先の~/var/www/html


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/migrate', methods=['POST'])
def migrate_data():
    try:
        # 旧サーバからデータを取得
        with old_db_engine.connect() as connection:
            old_tasks = connection.execute('SELECT * FROM tasks').fetchall()

        # 新サーバにデータを移行
        for task in old_tasks:
            if not NewTask.query.get(task.id):  # 重複チェック
                new_task = NewTask(
                    title=task.title,
                    description=task.description,
                    complete=task.complete
                )
                db.session.add(new_task)
        db.session.commit()

        return "データ移行が完了しました"

    except Exception as e:
        db.session.rollback()  # エラーが発生した場合、トランザクションをロールバック
        return f"データ移行中にエラーが発生しました: {e}"
    
def transfer():
    try:
        # /var/www/htmlの転送
        command = [f"rsync -avz {sending_directory} {recipiment_user}@{recipiment_IP}:{recipiment_directory}"]
        subprocess.run(command, check=True)
        return "転送完了"
    except subprocess.CalledProcessError:
        return "転送失敗"


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # テーブルを作成
    app.run(host="0.0.0.0", port=5000, debug=True)
