from flask import Flask, request, jsonify
import requests
from requests_oauthlib import OAuth1
from dotenv import load_dotenv
import base64
import os

# .envファイルから環境変数を読み込む
load_dotenv()

# OAuth 1.0a 認証情報を設定（環境変数から読み込む）
CONSUMER_API_KEY = os.getenv("CONSUMER_API_KEY")
CONSUMER_API_SECRET = os.getenv("CONSUMER_API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

# OAuth 1.0a 認証オブジェクトを作成
auth = OAuth1(CONSUMER_API_KEY, CONSUMER_API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

app = Flask(__name__)

def upload_image(image_url):
    """画像をアップロードし、media_id を取得する"""
    try:
        # 画像をバイナリデータとして取得
        response = requests.get(image_url)
        response.raise_for_status()  # エラーチェック
        image_data = response.content

        # Base64 エンコード
        image_base64 = base64.b64encode(image_data).decode('utf-8')

        # 画像をアップロード
        upload_url = "https://upload.twitter.com/1.1/media/upload.json"
        data = {"media_data": image_base64}
        response = requests.post(upload_url, auth=auth, data=data)  # auth を直接渡す
        response.raise_for_status()  # エラーチェック

        # media_id を取得
        media_id = response.json()["media_id_string"]
        return media_id

    except requests.exceptions.RequestException as e:
        print(f"Error fetching image or uploading to Twitter: {e}")
        return None
    except (KeyError, ValueError) as e:
        print(f"Error parsing Twitter response: {e}")
        return None

def post_tweet_with_image(text, media_id):
    """画像付きツイートを投稿する"""
    try:
        tweet_url = "https://api.twitter.com/2/tweets"
        payload = {
            "text": text,
            "media": {
                "media_ids": [media_id]
            }
        }
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        response = requests.post(tweet_url, headers=headers, json=payload)
        response.raise_for_status()  # エラーチェック
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error posting tweet: {e}")
        return None

@app.route("/", methods=["POST"])
def handle_post_request():
    """POSTリクエストを処理する"""
    try:
        print("Request Headers:", request.headers)  # デバッグ: リクエストヘッダーを出力
        print("Request Data:", request.data)  # デバッグ: リクエストデータを出力

        data = request.get_json()
        print("Parsed JSON Data:", data)  # デバッグ: 解析されたJSONデータを出力
        image_url = data["image_url"]

        media_id = upload_image(image_url)
        if media_id is None:
            return jsonify({"error": "Failed to upload image"}), 500
        print(f"Uploaded media ID: {media_id}")

        tweet_text = f"New image: {image_url}"
        tweet_response = post_tweet_with_image(tweet_text, media_id)
        if tweet_response is None:
            return jsonify({"error": "Failed to post tweet"}), 500
        print(f"Tweet Response: {tweet_response}")

        return jsonify({"message": "Tweet posted successfully!"}), 200

    except Exception as e:
        print(f"Error: {e}")  # デバッグ: エラーの詳細を出力
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True)