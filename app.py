from flask import Flask, render_template
from split_and_processing import process_and_send_files  # 関数のインポート
import time
import subprocess

app = Flask(__name__, static_folder='./templates/images')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/migrate', methods=['GET'])
def migrate():
    try:     
        # 1. 優先ファイル転送
        print("Starting pri_file_processing.py...")
        start_time = time.time()
        success, error = execute_script_with_output('pri_file_processing.py')
        elapsed_time = time.time() - start_time
        print(f"Completed pri_file_processing.py in {elapsed_time:.2f} seconds.")
        if not success:
            return render_template("index.html", complete=error)

        # 2. DB移動
        print("Starting db_processing.py...")
        start_time = time.time()
        success, error = execute_script_with_output('db_processing.py')
        elapsed_time = time.time() - start_time
        print(f"Completed db_processing.py in {elapsed_time:.2f} seconds.")
        if not success:
            return render_template("index.html", complete=error)

        # 3. その他のファイルを分割して送信
        print("Starting file processing and transfer...")
        start_time = time.time()
        shop_column_lists = ["cart", "info", "shop", "my-account", "checkout"]
        try:
            process_and_send_files(shop_column_lists, chunk_count=10)  # ファイル処理と送信を統合した関数を呼び出し
        except Exception as send_error:
            return render_template("index.html", complete=f"Error in file transfer: {send_error}")
        elapsed_time = time.time() - start_time
        print(f"Completed file processing and transfer in {elapsed_time:.2f} seconds.")

        # 全てのファイル転送の終了
        print("Migration process completed successfully!")
        return render_template("index.html", complete="Migration process completed successfully!")

    except Exception as error:
        print(f"Unexpected error: {error}")
        return render_template("index.html", complete=f"Unexpected error: {error}")


# コンソールに転送状況を出力
def execute_script_with_output(script_name):
    
    try:
        process = subprocess.Popen(
            ['python3', script_name],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        for line in process.stdout:
            print(line.strip()) 
        process.wait()
        if process.returncode != 0:
            for line in process.stderr:
                print(line.strip())
            return False, f"Error in {script_name}"
        return True, None
    except Exception as e:
        return False, f"Exception in {script_name}: {e}"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
