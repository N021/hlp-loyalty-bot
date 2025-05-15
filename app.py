from flask import Flask, request
import os
import requests
import openai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# 🔐 Токени
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

openai.api_key = OPENAI_API_KEY

# 🧠 Зберігаємо треди користувачів
user_threads = {}

@app.route("/")
def home():
    return "Bot is running"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]

        # Відповідаємо одразу, поки GPT думає
        send_message(chat_id, "✍️ Думаю над відповіддю...")

        # Отримуємо або створюємо thread для користувача
        thread_id = get_or_create_thread(chat_id)

        # Додаємо повідомлення користувача
        openai.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=text
        )

        # Запускаємо асистента
        run = openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )

        # Чекаємо завершення
        while True:
            status = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            if status.status == "completed":
                break
            elif status.status in ["failed", "cancelled", "expired"]:
                send_message(chat_id, "⚠️ Виникла помилка. Спробуйте ще раз.")
                return {"ok": True}
            time.sleep(1)

        # Отримуємо відповідь GPT
        messages = openai.beta.threads.messages.list(thread_id=thread_id)
        reply = next((msg.content[0].text.value for msg in reversed(messages.data) if msg.role == "assistant"), None)

        if reply:
            send_message(chat_id, reply)
        else:
            send_message(chat_id, "🤖 Не вдалося сформувати відповідь.")

    return {"ok": True}

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

def get_or_create_thread(user_id):
    if user_id not in user_threads:
        thread = openai.beta.threads.create()
        user_threads[user_id] = thread.id
    return user_threads[user_id]

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
