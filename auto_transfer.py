import json
import os
from file_transfer import rsync_wp_files
from get_files_for_tramsfer import get_files

def process_files(json_path):
    """
    data.jsonを処理し、ファイル転送を実行する。
    """
    while True:

        data = get_files()

        # データが空か確認
        if all(len(files) == 0 for files in data.values()):
            print("すべてのファイルが転送済みです。終了します。")
            break

        # 各カテゴリーのファイルを処理
        for category, files in data.items():
            if not files:
                continue

            # print(f"{category}カテゴリのファイルを転送します: {files_to_transfer}")
            print(f"{category}カテゴリのファイルを転送します: {files}")
            
            try:
                # rsync_wp_files({category: files_to_transfer})
                rsync_wp_files({category: files})
            except Exception as e:
                print(f"ファイル転送中にエラーが発生しました: {e}")


if __name__ == "__main__":
    # 処理開始
    process_files()
