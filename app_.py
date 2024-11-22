from flask import Flask, render_template
from db_processing import dump_wp_db, restore_wp_db
from file_processing import backup_wp_files, rsync_wp_files

app = Flask(__name__, static_folder='./templates/images')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/migrate', methods=['GET'])
def migrate():
    try:
        backup_wp_files()
        dump_wp_db()
        rsync_wp_files()
        restore_wp_db()
        complete = "Migration success"

    except Exception as error:
        complete = f"Error: {error}"
        
    return render_template("index.html", complete=complete)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
