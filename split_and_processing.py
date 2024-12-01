import subprocess
from file_transfer import rsync_wp_files  # ファイル送信関数をインポート


# ファイルを項目ごとに分割する関数
def organize_files_by_column(shop_column_lists):
    try:
        files_by_column = {}
        processed_files = set()

        # ファイル内を項目の文字列で検索する
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
                    line.strip()
                    for line in output_lines
                    # 分割する対象から除くディレクトリを記述
                    if "wp-content" not in line and "wp-includes" not in line and line.strip()
                ]
                files_by_column[shop_column] = file_paths
                processed_files.update(file_paths)
            else:
                print(f"Error executing command for '{shop_column}': {result.stderr}")
                files_by_column[shop_column] = []

        # どの項目の文字列も引っかからないファイルをotherとする
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


# 送るブロックごとに分ける関数
# 全体のファイル数を10回で転送する
def split_into_chunks(files_by_column, chunk_count=10):

    column_chunks = {column: [] for column in files_by_column.keys()}
    max_files = max(len(files) for files in files_by_column.values())

    for column, files in files_by_column.items():
        chunk_size = max(1, len(files) // chunk_count)
        for i in range(0, len(files), chunk_size):
            column_chunks[column].append(files[i:i + chunk_size])

    combined_chunks = []
    for i in range(chunk_count):
        chunk = {column: [] for column in files_by_column.keys()}
        for column, chunks in column_chunks.items():
            if i < len(chunks):
                chunk[column].extend(chunks[i])
        combined_chunks.append(chunk)

    return combined_chunks


# 送るブロックごとにファイルとそのパスをコンソールに出力
def process_and_send_files(shop_column_lists, chunk_count=10):
    files_by_column = organize_files_by_column(shop_column_lists)
    chunks = split_into_chunks(files_by_column, chunk_count)

    for idx, chunk in enumerate(chunks):
        print(f"----------------Chunk {idx + 1}----------------")
        for column, files in chunk.items():
            print(f"Column '{column}': {len(files)} files")
            for file in files:
                print(file)

        print(f"Sending files for Chunk {idx + 1}...")
        rsync_wp_files(chunk)
        print(f"Chunk {idx + 1} sent successfully.")


if __name__ == "__main__":
    shop_column_lists = ["cart", "info", "shop", "my-account", "checkout"]
    process_and_send_files(shop_column_lists, chunk_count=10)
