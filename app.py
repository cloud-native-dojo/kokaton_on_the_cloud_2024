from flask import Flask, request, jsonify, render_template
import os
from auto_transfer import process_files

app = Flask(__name__)

@app.route('/')
def user_page():
    return render_template("index.html")

@app.route('/admin', methods=['GET', 'POST'])
def admin_page():
    if request.method == 'POST':
        json_path = "data.json"
        csv_path = "tank_status.csv"
        try:
            json_path = "data.json"
            process_files(json_path)
            if os.path.exists(json_path):
                os.remove(json_path)
                os.remove(csv_path)
            return jsonify({"status": "Migration complete!"})
        except Exception as error:
            return jsonify({"status": f"Error: {error}"}), 500
    return render_template('admin.html')

if __name__ == '__main__':
    app.run(debug=True)
