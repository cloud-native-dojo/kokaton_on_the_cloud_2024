import json
import os
from file_transfer import rsync_wp_files
from get_files_for_tramsfer import get_files

def load_data(json_path):
    """
    JSONファイルをロードして辞書を返す。
    """
    with open(json_path, 'r') as file:
        return json.load(file)

def save_data(json_path, data):
    """
    辞書データをJSONファイルに保存する。
    """
    with open(json_path, 'w') as file:
        json.dump(data, file, indent=4)

def process_files(json_path):
    """
    data.jsonを処理し、ファイル転送を実行する。
    """
    while True:
        # JSONデータをロード
        if not os.path.exists(json_path):
            print("data.jsonが見つかりません。処理を終了します。")
            break
        
        data = load_data(json_path)

        # データが空か確認
        if all(len(files) == 0 for files in data.values()):
            print("すべてのファイルが転送済みです。終了します。")
            break

        # 各カテゴリーのファイルを処理
        for category, files in data.items():
            if not files:
                continue

            # 転送するファイルを選択（適当に5個ずつ）
            files_to_transfer = files[:5]

            print(f"{category}カテゴリのファイルを転送します: {files_to_transfer}")
            
            try:
                rsync_wp_files({category: files_to_transfer})
            except Exception as e:
                print(f"ファイル転送中にエラーが発生しました: {e}")

            # 転送済みのファイルを削除
            data[category] = files[5:]

        # 更新されたデータを保存
        save_data(json_path, data)



if __name__ == "__main__":
    # data.jsonのパスを指定
    json_path = "data.json"

    # 処理開始
    process_files(json_path)
