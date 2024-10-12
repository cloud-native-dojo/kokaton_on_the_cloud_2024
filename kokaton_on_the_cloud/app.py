from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'  # SQLiteデータベースのURI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 変更トラッキング機能を無効化
db = SQLAlchemy(app)


# データベースモデル定義
class Todo(db.Model):
    """
    Todoデータベースモデルクラス。
    Attributes:
    -----------
    id : int
        プライマリキー、todoアイテムの一意なID。
    title : str
        Todoアイテムのタイトル。
    complete : bool
        Todoアイテムが完了したかどうかを示すフラグ。
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))  # 入力可能な最大文字数を100と設定
    complete = db.Column(db.Boolean)  # 完了ステータス（True/False）

@app.route("/")
def index():
    """
    ルートURLの処理を担当する関数。\n
    データベースから全てのtodoアイテムを取得し、HTMLテンプレートに渡して表示する。
    
    Returns:
    --------
    str
        レンダリングされたHTMLテンプレート。
    """
    todo_list = Todo.query.all()  # 全ての項目のリスト(レコード)を取得
    return render_template('index.html', todo_list=todo_list)

@app.route("/about")
def about():
    """
    /about URLにアクセスされた際に呼び出される関数。\n
    "About"というテキストを返す。

    Returns:
    --------
    str
        "About"という文字列。
    """
    return "About"

@app.route("/add", methods=["POST"])
def add_todo():
    """
    新しいTodoアイテムをデータベースに追加する処理を担当する関数。\n
    フォームデータからタイトルを取得し、新しいTodoオブジェクトを作成し、データベースに追加する。

    Returns:
    --------
    redirect
        トップページ（Todoリスト）へリダイレクト。
    """
    title = request.form.get("title")  # フォームからタイトルを取得
    new_todo = Todo(title=title, complete=False)  # 新しいtodoを作成
    db.session.add(new_todo)  # データベースに追加
    db.session.commit()  # 変更をコミット
    return redirect(url_for("index"))  # トップページへリダイレクト

@app.route("/update/<int:todo_id>")
def update_todo(todo_id):
    """
    指定されたTodoアイテムの完了ステータスを切り替える処理を行う関数。\n
    完了していない場合は完了済みに、完了済みの場合は未完了に変更する。

    Parameters:
    -----------
    todo_id : int
        更新対象のTodoアイテムのID。

    Returns:
    --------
    redirect
        トップページ（Todoリスト）へリダイレクト。
    """
    todo = Todo.query.filter_by(id=todo_id).first()  # 指定IDのtodoを取得
    todo.complete = not todo.complete  # 完了ステータスをトグル
    db.session.commit()  # 変更をコミット
    return redirect(url_for("index"))  # トップページへリダイレクト

@app.route("/delete/<int:todo_id>")
def delete_todo(todo_id):
    """
    指定されたTodoアイテムをデータベースから削除する関数。
    
    Parameters:
    -----------
    todo_id : int
        削除対象のTodoアイテムのID。

    Returns:
    --------
    redirect
        トップページ（Todoリスト）へリダイレクト。
    """
    todo = Todo.query.filter_by(id=todo_id).first()  # 指定IDのtodoを取得
    db.session.delete(todo)  # データベースから削除
    db.session.commit()  # 変更をコミット
    return redirect(url_for("index"))  # トップページへリダイレクト

# アプリケーションのエントリーポイント
if __name__ == "__main__":
    """
    アプリケーションのエントリーポイント。\n
    アプリケーションコンテキストを作成し、データベースを初期化する。
    """
    with app.app_context():
        db.create_all()  # データベースのテーブルを作成
    
    app.run(debug=True)  # デバッグモードでアプリケーションを実行
