from flask import Flask, request
import os
import requests

app = Flask(__name__)

# Отримай токен з середовища
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

@app.route("/")
def home():
    return "Bot is running"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    # обробка лише повідомлень
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]

        # приклад відповіді
        reply_text = f"Ви написали: {text}"
        send_message(chat_id, reply_text)

    return {"ok": True}

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

# 🛠️ ОБОВ'ЯЗКОВО правильне порівняння тут:
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
