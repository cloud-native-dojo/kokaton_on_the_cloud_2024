from flask import Flask, request, jsonify, render_template
import os
from auto_transfer import process_files
import csv
from pri_file_processing import pri_rsync_wp_files
from file_remove import all_remove
from db_processing import dump_wp_db, restore_wp_db
import count_access
import threading

app = Flask(__name__)

score_update_thread = None

# スコアを定期的に更新するスレッド
def update_scores():
    while True:
        count_access.write()  # count_accessのwrite処理を呼び出し

pri_func_comp = False
# variable_is_true = False
json_path = "data.json"
csv_path = "tank_status.csv"
access_path = "access_counts.csv"

if os.path.exists(json_path):
    os.remove(json_path)
    os.remove(csv_path)
    os.remove(access_path)

@app.route('/')
def user_page():
    return render_template("index.html")


# @app.route('/check-variable', methods=['GET'])
# def check_variable():
#     if variable_is_true:
#         # Trueならリダイレクト先を指定
#         return jsonify({'redirect': True, 'url': 'http://10.204.227.151:30080'})
#     else:
#         # Falseならそのまま
#         return jsonify({'redirect': False})


@app.route('/progress', methods=['GET'])
def get_progress():
    csv_path = "tank_status.csv"  # CSVファイルのパス
    if not os.path.exists(csv_path):
        return jsonify({"error": "CSV file not found"}), 404

    progress_data = []
    try:
        with open(csv_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                progress_data.append({"path":  f"http://10.204.227.151:30080{row['Path']}", "value": int(row["Value"])})
        return jsonify(progress_data)
    except Exception as error:
        return jsonify({"error": f"Error reading CSV: {error}"}), 500

@app.route('/check-status', methods=['GET'])
def check_status():
    global pri_func_comp
    return jsonify({"completed": pri_func_comp})

@app.route('/admin', methods=['GET', 'POST'])
def admin_page():
    global pri_func_comp, score_update_thread
    pri_func_comp = False
    # variable_is_true = False

    if request.method == 'POST':
        try:
            all_remove()
            dump_wp_db()
            restore_wp_db()
            if score_update_thread is None or not score_update_thread.is_alive():
                update_thread = threading.Thread(target=update_scores, daemon=True)
                update_thread.start()
                print("Score update thread started")
            pri_rsync_wp_files()
            pri_func_comp = True
            process_files()
            # variable_is_true = True
            if os.path.exists(json_path):
                os.remove(json_path)
                os.remove(csv_path)
            return jsonify({"status": "Migration complete!"})
        except Exception as error:
            return jsonify({"status": f"Error: {error}"}), 500
    return render_template('admin.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
