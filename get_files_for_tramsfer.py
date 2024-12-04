def get_files():
    import subprocess
    import pandas as pd
    import numpy as np
    import json
    import os
    import score

    def organize_files_by_column(shop_column_lists):
        """
        指定された項目に関連するファイルを取得し、辞書形式で返す。
        どの項目にも該当しないファイルは "other" に分類される。
        """
        try:
            files_by_column = {}
            processed_files = set()

            # 各項目に関連するファイルを取得
            for shop_column in shop_column_lists:
                command = [
                    "kubectl", "exec", "-i", "-n", "before-migration",
                    "deploy/before-wordpress", "--", "sh", "-c",
                    f"grep -r '{shop_column}' /var/www/html | awk -F':' '{{print $1}}' | sort | uniq"
                ]
                result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if result.returncode == 0 and result.stdout:
                    output_lines = result.stdout.strip().split("\n")
                    file_paths = [
                        line.strip() for line in output_lines
                        if "wp-content" not in line and "wp-includes" not in line and line.strip()
                    ]
                    files_by_column[shop_column] = file_paths
                    processed_files.update(file_paths)
                else:
                    print(f"Error executing command for '{shop_column}': {result.stderr}")
                    files_by_column[shop_column] = []

            # "other" に分類されるファイルを取得
            all_files_command = [
                "kubectl", "exec", "-i", "-n", "before-migration",
                "deploy/before-wordpress", "--", "sh", "-c",
                "find /var/www/html -type f | grep -v 'wp-content' | grep -v 'wp-includes'"
            ]
            result = subprocess.run(all_files_command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0 and result.stdout:
                all_files = result.stdout.strip().split("\n")
                other_files = [file for file in all_files if file not in processed_files]
                files_by_column["other"] = other_files
            else:
                print(f"Error fetching all files: {result.stderr}")
                files_by_column["other"] = []

            return files_by_column
        except Exception as e:
            print(f"An error occurred: {e}")
            return {}

    def adjust_to_sum_10(values):
        """
        配列内の値を丸めて合計が10になるように調整する。
        """
        rounded_values = np.floor(values).astype(int)
        total = rounded_values.sum()
        errors = values - rounded_values

        while total < 30:
            max_error_index = np.argmax(errors)
            rounded_values[max_error_index] += 1
            # errors[max_error_index] = -np.inf  # 調整済みの値を除外
            total += 1

        while total > 30:
            min_error_index = np.argmin(errors)
            rounded_values[min_error_index] -= 1
            # errors[min_error_index] = np.inf  # 調整済みの値を除外
            total -= 1

        return rounded_values

    def manage_json(file_path, data_dict, item_counts):
        """
        JSONファイルを管理し、指定された数のファイルパスを取得・削除する。

        Parameters:
        - file_path: str, JSONファイルのパス
        - data_dict: dict, 項目とファイルパスの辞書
        - item_counts: dict, {item: count}形式の項目と取得数の指定

        Returns:
        - dict, {item: [取得されたファイルパス]}形式の辞書
        """
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
            print(f"既存のJSONファイルを読み込みました: {file_path}")
        else:
            data = data_dict
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"JSONファイルを作成しました: {file_path}")
            
        
        result = {}
        for item, count in item_counts.items():
            if item not in data:
                raise ValueError(f"指定された項目 '{item}' は存在しません。")
            
            file_paths = data[item]
            if count > len(file_paths):
                count = len(file_paths)
                change_tank(item)
                # raise ValueError(f"項目 '{item}' の取得数が多すぎます。指定可能: {len(file_paths)}")
            
            extracted_paths = file_paths[:count]
            data[item] = file_paths[count:]
            result[item] = extracted_paths
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        
        return result

    def change_tank(col):
        file_path = "tank_status.csv"
        df=pd.read_csv(file_path)
        df.loc[df['Path'] == f'/{col}', 'Value'] = 1
        df.to_csv(file_path, index=False)

    # メイン処理
    shop_column_lists = ["cart", "info", "shop", "my-account", "checkout"]
    file_path = "data.json"
    dct = score.num()
    keys, values = list(dct.keys()), np.array(list(dct.values())) * 30
    item_count = {}
    if not np.all(values == [0, 0, 0, 0, 0]):
        result = adjust_to_sum_10(values)

        item_counts = {key: value for key, value in zip(keys, result)}
        for page, count in item_counts.items():
            if page == "pay":
                page = "checkout"
            elif page == "account":
                page = "my-account"
            elif page == "items":
                page = "shop"
            item_count[page] = count
    else:
        item_count["other"] = 328

    print("送るファイルの数")
    print(item_count)
    print()

    if not os.path.exists(file_path):
        files_by_column = organize_files_by_column(shop_column_lists)
        try:
            extracted_paths = manage_json(file_path, files_by_column, item_count)
            print(f"取得されたファイルパスを送ります")
            return extracted_paths
        except ValueError as e:
            print(f"エラー: {e}")
    else:
        try:
            extracted_paths = manage_json(file_path, {}, item_count)
            print(f"取得されたファイルパスを送ります")
            return extracted_paths
        except ValueError as e:
            print(f"エラー: {e}")

if __name__ == "main":
    get_files()