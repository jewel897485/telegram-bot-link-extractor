from flask import Flask, request
import re
import requests

# ✅ Bot Token
TOKEN = "8116086574:AAGP-4fibBwa4DqmGdTiIDmjijUioGh12xM"
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

# ✅ Google Sheet Web App URL
GOOGLE_SHEET_WEBHOOK = "https://script.google.com/macros/s/AKfycbwkMMe401QPlBeOsypfnxu_qXcJB5qjq5Y_P7q3WXASj8FdCjHAtq3ZWRt-6_hJMiCsvQ/exec"

# ✅ Google Sheet Checker URL (new endpoint to check if URL already exists)
GOOGLE_SHEET_CHECK_URL = "https://script.google.com/macros/s/AKfycbwkMMe401QPlBeOsypfnxu_qXcJB5qjq5Y_P7q3WXASj8FdCjHAtq3ZWRt-6_hJMiCsvQ/exec?action=check&url="

app = Flask(__name__)

# 🔍 Extract only URL from message
def extract_url(text):
    match = re.search(r'https?://\S+', text)
    return match.group(0) if match else None

# ✅ Check if link already exists in Google Sheet
def is_duplicate(url):
    try:
        response = requests.get(GOOGLE_SHEET_CHECK_URL + url)
        return response.text.strip() == "exists"
    except:
        return False

# 📥 Handle Telegram Webhook
@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()

    if 'message' in data and 'text' in data['message']:
        chat_id = data['message']['chat']['id']
        message_id = data['message']['message_id']
        text = data['message']['text']
        url = extract_url(text)

        if url:
            # ✅ Reply with only the link
            requests.post(TELEGRAM_API, json={"chat_id": chat_id, "text": url})
            
            # ✅ Check duplicate and then send to Google Sheet
            if not is_duplicate(url):
                requests.post(GOOGLE_SHEET_WEBHOOK, json={"url": url})
            
            # ✅ Delete original message
            requests.post(f"https://api.telegram.org/bot{TOKEN}/deleteMessage", json={
                "chat_id": chat_id,
                "message_id": message_id
            })

    return "OK", 200

@app.route('/', methods=['GET'])
def index():
    return "Bot is running ✅", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
