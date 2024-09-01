from flask import Flask, request
import tweepy
from dotenv import load_dotenv
import os

# .envファイルから環境変数を読み込む
load_dotenv()

app = Flask(__name__)

# Twitter APIの認証情報を環境変数から取得
API_KEY = os.getenv('API_KEY')
API_SECRET_KEY = os.getenv('API_SECRET_KEY')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')

# Tweepyで認証
auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# ルートエンドポイントを定義
@app.route('/post-image', methods=['GET'])
def post_image():
    image_url = request.args.get('image_url')
    if image_url:
        try:
            # Twitterに画像を投稿
            api.update_status(status="Image from Bot", media_urls=[image_url])
            return "Image posted successfully!"
        except Exception as e:
            return f"Error: {e}"
    else:
        return "No image URL provided!"

if __name__ == '__main__':
    app.run(port=5000)
