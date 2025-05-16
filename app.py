from flask import Flask, request
import os
import requests
import openai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Токени
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
openai.api_key = OPENAI_API_KEY

# Стани користувачів
user_states = {}  # {chat_id: {"step": int, "answers": dict}}

@app.route("/")
def home():
    return "Bot is running"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"].strip()

        # Ініціалізація нового користувача
        if chat_id not in user_states or text == "/start":
            user_states[chat_id] = {"step": 1, "answers": {}}
            send_message(chat_id, "*Питання 1/4*\n*У яких регіонах світу ви плануєте подорожувати?*\n(Можна обрати декілька варіантів або вказати конкретну країну/країни.)\n1. Європа\n2. Північна Америка\n3. Азія\n4. Близький Схід\n5. Африка\n6. Південна Америка\n7. Карибський басейн\n8. Океанія\n9. Мене цікавлять лише деякі країни (вкажіть які)", markdown=True)
            return {"ok": True}

        step = user_states[chat_id]["step"]

        if step == 1:
            user_states[chat_id]["answers"]["regions"] = text
            user_states[chat_id]["step"] = 2
            send_message(chat_id, "*Питання 2/4*\n*Яку категорію готелів ви зазвичай обираєте?*\n1. Luxury (преміум-клас)\n2. Comfort (середній клас)\n3. Essential (економ-клас)", markdown=True)

        elif step == 2:
            if text.lower() not in ["luxury", "comfort", "essential"]:
                send_message(chat_id, "❗️ Будь ласка, оберіть лише один із запропонованих варіантів: Luxury, Comfort або Essential.")
                return {"ok": True}
            user_states[chat_id]["answers"]["category"] = text
            user_states[chat_id]["step"] = 3
            send_message(chat_id, "*Питання 3/4*\n*Який стиль готелю ви зазвичай обираєте?* (Оберіть до трьох варіантів.)\n1. Розкішний і вишуканий\n2. Бутік і унікальний\n3. Класичний і традиційний\n4. Сучасний і дизайнерський\n5. Затишний і сімейний\n6. Практичний і економічний", markdown=True)

        elif step == 3:
            user_states[chat_id]["answers"]["style"] = text
            user_states[chat_id]["step"] = 4
            send_message(chat_id, "*Питання 4/4*\n*З якою метою ви зазвичай зупиняєтеся в готелі?* (Оберіть до двох варіантів.)\n1. Бізнес-подорожі / відрядження\n2. Відпустка / релакс\n3. Сімейний відпочинок\n4. Довготривале проживання", markdown=True)

        elif step == 4:
            user_states[chat_id]["answers"]["purpose"] = text
            send_message(chat_id, "✅ Дякую! Я опрацюю вашу інформацію й надам рекомендації.")
            user_states[chat_id]["step"] = 5  # завершення
        else:
            send_message(chat_id, "🤖 Очікую команду або введення /start для перезапуску.")

    return {"ok": True}

def send_message(chat_id, text, markdown=False):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown" if markdown else None,
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    # Встановлюємо Webhook
    webhook_url = "https://hlp-loyalty-bot.onrender.com/webhook"
    set_webhook_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook"
    r = requests.post(set_webhook_url, data={"url": webhook_url})
    print(f"Webhook status: {r.status_code}, response: {r.text}")

    # Запускаємо Flask
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
