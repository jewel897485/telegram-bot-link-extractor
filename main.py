from flask import Flask, request
import re
import requests

# ✅ আপনার Bot Token
TOKEN = "8116086574:AAGP-4fibBwa4DqmGdTiIDmjijUioGh12xM"
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

# ✅ Google Sheet Web App URL
GOOGLE_SHEET_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbwkMMe401QPlBeOsypfnxu_qXcJB5qjq5Y_P7q3WXASj8FdCjHAtq3ZWRt-6_hJMiCsvQ/exec"

app = Flask(__name__)

# 🔍 হেডলাইনসহ মেসেজ থেকে কেবল লিংক বের করা
def extract_url(text):
    match = re.search(r'https?://\S+', text)
    return match.group(0) if match else None

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()

    if 'message' in data and 'text' in data['message']:
        message = data['message']
        chat_id = message['chat']['id']
        message_id = message['message_id']
        text = message['text']
        url = extract_url(text)

        if url:
            # ✅ 1. ইউজারকে শুধু লিংক রেপ্লাই করা
            requests.post(f"{TELEGRAM_API}/sendMessage", json={
                "chat_id": chat_id,
                "text": url
            })

            # ✅ 2. মূল মেসেজটি ডিলিট করা
            requests.post(f"{TELEGRAM_API}/deleteMessage", json={
                "chat_id": chat_id,
                "message_id": message_id
            })

            # ✅ 3. Google Sheet এ লিংক পাঠানো
            requests.post(GOOGLE_SHEET_WEBAPP_URL, json={"url": url})

    return "OK", 200

@app.route('/', methods=['GET'])
def index():
    return "🤖 Bot is running!", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
