from flask import Flask, request, jsonify
import requests
import openai
import os

app = Flask(__name__)

# 設定 OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# 設定 Line API Token
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
LINE_API_URL = "https://api.line.me/v2/bot/message/reply"

@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.json
    events = body.get("events", [])
    
    for event in events:
        if event.get("type") == "message" and event["message"].get("type") == "text":
            reply_token = event["replyToken"]
            user_message = event["message"]["text"]

            # 取得 AI 回應
            ai_response = get_ai_response(user_message)

            # 回覆到 Line
            reply_message(reply_token, ai_response)

    return jsonify({"status": "ok"})

def get_ai_response(user_message):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_message}]
    )
    return response["choices"][0]["message"]["content"]

def reply_message(reply_token, text):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}",
    }
    data = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": text}],
    }
    requests.post(LINE_API_URL, headers=headers, json=data)

if __name__ == "__main__":
    app.run()
