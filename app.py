from flask import Flask, request, jsonify, render_template
import os
from auto_transfer import process_files
import csv
from pri_file_processing import pri_rsync_wp_files
from file_remove import all_remove
from db_processing import dump_wp_db, restore_wp_db

app = Flask(__name__)

pri_func_comp = False

@app.route('/')
def user_page():
    return render_template("index.html")

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
                progress_data.append({"path": row["Path"], "value": int(row["Value"])})
        return jsonify(progress_data)
    except Exception as error:
        return jsonify({"error": f"Error reading CSV: {error}"}), 500

@app.route('/check-status', methods=['GET'])
def check_status():
    global pri_func_comp
    return jsonify({"completed": pri_func_comp})

@app.route('/admin', methods=['GET', 'POST'])
def admin_page():
    global pri_func_comp
    if request.method == 'POST':
        json_path = "data.json"
        csv_path = "tank_status.csv"
        try:
            if os.path.exists(json_path):
                os.remove(json_path)
                os.remove(csv_path)
            all_remove()
            dump_wp_db()
            restore_wp_db()
            pri_rsync_wp_files()
            pri_func_comp = True
            process_files()
            if os.path.exists(json_path):
                os.remove(json_path)
                os.remove(csv_path)
            return jsonify({"status": "Migration complete!"})
        except Exception as error:
            return jsonify({"status": f"Error: {error}"}), 500
    return render_template('admin.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
