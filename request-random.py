import requests
import random
import time

# URLリスト
urls = [
    "http://10.204.227.151:30080/cart/",
    "http://10.204.227.151:30080/sample-page/",
    "http://10.204.227.151:30080/shop/",
    "http://10.204.227.151:30080/my-account/",
    "http://10.204.227.151:30080/cart/"
]

try:
    while True:
        # ランダムにURLを選択
        url = random.choice(urls)
        try:
            # GETリクエストを送信
            response = requests.get(url)
            print(f"Accessed {url} - Status Code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            # エラーが発生した場合のログ
            print(f"Error accessing {url}: {e}")
        
        # 次のリクエストまでの待機時間（0.1〜1秒）
        wait_time = random.uniform(0.1, 1)
        time.sleep(wait_time)

except KeyboardInterrupt:
    print("\nStopping random URL access.")
