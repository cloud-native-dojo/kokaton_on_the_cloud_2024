import requests
import subprocess
import re
import random
import time
from datetime import datetime, timedelta

# アクセスする対象のURLとページリスト
base_url = "http://10.204.227.151:30080/"  # サイトのURLに置き換えてください
pages = ["cart", "sample-page", "shop"]  # 各ページのパスに置き換えてください
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

# ログからアクセス数を集計
# def count_accesses(logs):
#     access_pattern = re.compile(r"GET\s(/(?:shop|cart|sample-page))")
#     matches = re.findall(access_pattern, logs)

#     access_counts = {}
#     for match in matches:
#         if match in access_counts:
#             access_counts[match] += 1
#         else:
#             access_counts[match] = 1

#     return access_counts

def count_accesses_within_last_minute(logs):
    # 特定のパスと時間の抽出用の正規表現
    # access_pattern = re.compile(r'\[(\d+/[A-Za-z]+/\d+:\d{2}:\d{2}:\d{2})\s[+\-]\d{4}]\s"GET\s(/(?:shop|cart|sample-page))')
    access_pattern = re.compile(r'\[(\d+/[A-Za-z]+/\d+:\d{2}:\d{2}:\d{2})\s[+\-]\d{4}]\s"GET\s(/(?:shop|cart|sample-page))\sHTTP/1.1"\s\d+\s\d+\s"-"\s"python-requests/[\d\.]+"')

    # 現在の時刻を基準に1分前の時刻を計算
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=1)

    access_counts = {}
    for line in logs.splitlines():
        match = access_pattern.search(line)
        if match:
            # マッチした時間とパスを取得
            log_time_str, path = match.groups()
            
            # ログの時間を `"%d/%b/%Y:%H:%M:%S"` 形式でパース
            log_time = datetime.strptime(log_time_str, "%d/%b/%Y:%H:%M:%S")
            
            # ログの時間が指定の範囲内かチェック
            if start_time <= log_time <= end_time:
                if path in access_counts:
                    access_counts[path] += 1
                else:
                    access_counts[path] = 1

    return access_counts


# 実行例
if __name__ == "__main__":
    pod_name = get_pod_name("before-wordpress")  # 対象のPod名に置き換えてください
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

    # Podを再起動してログを初期化
    # restart_pod(pod_name)