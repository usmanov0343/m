from flask import Flask, request
import requests
import os
import json

TOKEN = "8163972507:AAEL9ZSxZzaifHM-fGuG29APu6yp5s0tjS8"  # TOKENni to'g'ridan-to'g'ri yozing
URL = f"https://api.telegram.org/bot{TOKEN}/"
ADMIN_ID = 6688570192

app = Flask(__name__)

POEM_FILE = "poems.json"  # Railway uchun oddiy fayl bo'lsin

def load_poems():
    if not os.path.exists(POEM_FILE):
        with open(POEM_FILE, "w") as f:
            json.dump({"poems": []}, f)
    with open(POEM_FILE, "r") as f:
        return json.load(f)["poems"]

def save_poem(text):
    poems = load_poems()
    poems.append(text)
    with open(POEM_FILE, "w") as f:
        json.dump({"poems": poems}, f)

def send_message(chat_id, text, markup=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": markup,
        "parse_mode": "Markdown"
    }
    requests.post(URL + "sendMessage", json=payload)

admin_waiting_for_poem = {}

@app.route("/", methods=["GET"])
def home():
    return "Bot is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if not data:
        return "OK"

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # Admin she'r kiritayotgan bo'lsa
        if chat_id in admin_waiting_for_poem:
            save_poem(text)
            del admin_waiting_for_poem[chat_id]
            send_message(chat_id, "✅ *She’r muvaffaqiyatli qo‘shildi!*")
            return "OK"

        # /start
        if text == "/start":
            if chat_id == ADMIN_ID:
                keyboard = {
                    "keyboard": [
                        [{"text": "📜 She’rlar ro‘yxati"}],
                        [{"text": "📥 Yangi she’r qo‘shish"}]
                    ],
                    "resize_keyboard": True
                }
                send_message(chat_id, "Admin panel:", keyboard)
            else:
                poems = load_poems()
                keyboard = {"keyboard": [], "resize_keyboard": True}
                for i in range(len(poems)):
                    keyboard["keyboard"].append([{"text": f"📘 She’r {i+1}"}])
                if not keyboard["keyboard"]:
                    send_message(chat_id, "Hozircha she’rlar yo‘q.")
                else:
                    send_message(chat_id, "She’rni tanlang:", keyboard)
            return "OK"

        # Yangi she'r
        if text == "📥 Yangi she’r qo‘shish" and chat_id == ADMIN_ID:
            admin_waiting_for_poem[chat_id] = True
            send_message(chat_id, "Yangi she’r matnini yuboring:")
            return "OK"

        # She’r ro‘yxati
        if text == "📜 She’rlar ro‘yxati" and chat_id == ADMIN_ID:
            poems = load_poems()
            if not poems:
                send_message(chat_id, "Hozircha she’rlar yo‘q.")
                return "OK"
            msg = "*She’rlar ro‘yxati:*\n\n"
            for i, p in enumerate(poems, start=1):
                msg += f"{i}. {p[:30]}...\n"
            send_message(chat_id, msg)
            return "OK"

        # She’r ko‘rish
        if text.startswith("📘 She’r "):
            try:
                index = int(text.replace("📘 She’r ", "")) - 1
                poems = load_poems()
                send_message(chat_id, poems[index])
            except:
                send_message(chat_id, "❌ She’r topilmadi")
            return "OK"

    return "OK"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)


