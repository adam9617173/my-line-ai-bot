from flask import Flask, request, jsonify
import requests
import openai
import os

app = Flask(__name__)

# 設定 OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")

if not OPENAI_API_KEY or not LINE_ACCESS_TOKEN:
    raise ValueError("API Key 未設定，請確認 Vercel 環境變數！")

@app.route("/")
def home():
    return "Line AI Bot is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        body = request.json
        if not body:
            return jsonify({"error": "Invalid request"}), 400

        events = body.get("events", [])
        
        for event in events:
            if event.get("type") == "message" and event["message"].get("type") == "text":
                reply_token = event["replyToken"]
                user_message = event["message"]["text"]

                # 取得 AI 回應
                ai_response = get_ai_response(user_message)

                # 回覆到 Line
                reply_message(reply_token, ai_response)

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print(f"錯誤：{str(e)}")  # 印出錯誤訊息到 Vercel Log
        return jsonify({"error": "Webhook 內部錯誤", "message": str(e)}), 500

def get_ai_response(user_message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"AI 回應錯誤：{str(e)}"

def reply_message(reply_token, text):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}",
    }
    data = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": text}],
    }
    response = requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=data)

    if response.status_code != 200:
        print(f"Line API 回應錯誤：{response.text}")

if __name__ == "__main__":
    app.run()
