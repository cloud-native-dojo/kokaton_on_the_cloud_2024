def write():
    import requests
    import subprocess
    import re
    import random
    import time
    from datetime import datetime, timedelta
    import csv
    from collections import defaultdict

    # アクセスする対象のURLとページリスト
    base_url = "http://10.204.227.151:30080/"  # サイトのURLに置き換えてください
    pages = ["cart", "info", "shop","my-account","checkout"]  # 各ページのパスに置き換えてください
    # pages = ["cart"]  # 各ページのパスに置き換えてください

    # 指定したページにランダムな間隔でアクセス
    def random_access_pages(duration_seconds):
        start_time = time.time()
        while time.time() - start_time < duration_seconds:
            page = random.choice(pages)  # ランダムなページを選択
            url = f"{base_url}{page}"
            try:
                response = requests.get(url)
                print(f"Accessed {url}: Status {response.status_code}")
            except requests.RequestException as e:
                print(f"Error accessing {url}: {e}")
            
            # 次のアクセスまでランダムに0.5〜3秒間隔を空ける
            time.sleep(random.uniform(0.5, 3))

    def get_pod_name(deployment_name, namespace="before-migration"):
        try:
            result = subprocess.run(
                ["kubectl", "get", "pods", "-n", namespace, "-l", f"app={deployment_name}", "-o", "jsonpath={.items[0].metadata.name}"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Error fetching pod name: {e}")
            return None

    # kubectl logsでPodのログを取得
    def get_kubectl_logs(pod_name, namespace="before-migration"):
        try:
            result = subprocess.run(
                ["kubectl", "logs", pod_name, "-n", namespace],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error fetching logs: {e}")
            return None

    def append_to_csv(access_counts, logs):
        # CSVファイルのパス
        csv_file = 'access_counts.csv'

        # CSVファイルが存在するか確認
        file_exists = False
        try:
            with open(csv_file, mode='r', newline='') as f:
                file_exists = True
        except FileNotFoundError:
            file_exists = False

        # CSVファイルを追記モードで開く
        with open(csv_file, mode='a', newline='') as f:
            writer = csv.writer(f)

            # ヘッダーを書き込む（初回のみ）
            if not file_exists:
                writer.writerow(['Timestamp', 'Path', 'Access Count'])
                access_counts_before, log_time = count_accesses_before(logs)
                for path, count in access_counts_before.items():
                    if path == "/sample-page":
                        path = "/info"
                    writer.writerow([log_time, path, count])

            # 現在のタイムスタンプを取得
            timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

            if access_counts:
                # アクセス数をCSVに追記
                for path, count in access_counts.items():
                    writer.writerow([timestamp, path, count])

    def count_accesses_before(logs):
        access_pattern = re.compile(r'\[(\d+/[A-Za-z]+/\d+:\d{2}:\d{2}:\d{2})\s[+\-]\d{4}]\s"GET\s(/(?:shop|cart|sample-page|my-account|checkout))\sHTTP/1.1"\s\d+\s\d+\s"-"\s"python-requests/[\d\.]+"')

        # 現在の時刻を基準に1分前の時刻を計算
        end_time = datetime(2024, 11, 18, 14, 30)  # ここで時間を設定
        start_time = datetime(2024, 11, 18, 2, 0)  # ここで時間を設定

        access_counts_before = defaultdict(int)
        for line in logs.splitlines():
            match = access_pattern.search(line)
            if match:
                # マッチした時間とパスを取得
                log_time_str, path = match.groups()
                
                # ログの時間を `"%d/%b/%Y:%H:%M:%S"` 形式でパース
                log_time = datetime.strptime(log_time_str, "%d/%b/%Y:%H:%M:%S")
                
                # ログの時間が指定の範囲内かチェック
                if start_time <= log_time <= end_time:
                    access_counts_before[path] += 1
        return access_counts_before, log_time

    def count_accesses_within_last_minute(logs):
        # 特定のパスと時間の抽出用の正規表現
        access_pattern = re.compile(r'\[(\d+/[A-Za-z]+/\d+:\d{2}:\d{2}:\d{2})\s[+\-]\d{4}]\s"GET\s(/(?:shop|cart|info|my-account|checkout))\sHTTP/1.1"\s\d+\s\d+\s"-"\s"python-requests/[\d\.]+"')

        # 現在の時刻を基準に1分前の時刻を計算
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=1)

        access_counts = defaultdict(int)
        for line in logs.splitlines():
            match = access_pattern.search(line)
            if match:
                # マッチした時間とパスを取得
                log_time_str, path = match.groups()
                
                # ログの時間を `"%d/%b/%Y:%H:%M:%S"` 形式でパース
                log_time = datetime.strptime(log_time_str, "%d/%b/%Y:%H:%M:%S")
                
                # ログの時間が指定の範囲内かチェック
                if start_time <= log_time <= end_time:
                    access_counts[path] += 1
            # 集計した結果をCSVファイルに追記
        append_to_csv(access_counts, logs)

        return access_counts

    # 実行例
    if __name__ == "count_access":
        pod_name = get_pod_name("before-wordpress")  # 対象のPod名に置き換えてください
        print(pod_name)
        access_duration = 60  # アクセスの継続時間（秒）

        # ランダムアクセスを開始
        print("Starting random access...")
        random_access_pages(access_duration)

        # アクセス終了後に少し待機
        time.sleep(2)

        # ログを取得してアクセス数を集計
        logs = get_kubectl_logs(pod_name)
        if logs:
            access_counts = count_accesses_within_last_minute(logs)
            print("\nPage Access Counts:")
            for page, count in access_counts.items():
                print(f"{page}: {count} accesses")