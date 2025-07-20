from fastapi import FastAPI, Request, HTTPException
import httpx
import os

# ✅ CONFIGURATION
BOT_TOKEN = "6650907198:AAE8Vh7spwH3O1gikm64UpLPJgnAqw8yZNo"  # Put your bot token here
WEBHOOK_SECRET = "ndtv"  # Your chosen webhook secret path
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwoq2rokXRRIwFr60OKqJI8MhtvVpIepxCKZ9A-n7CV_COxQIdsMiKQ5EoMhPIkn7K3bw/exec"

# ✅ ONLY ALLOW THESE TELEGRAM USER IDs
ALLOWED_USER_IDS = [1414414216]

# ✅ INIT
app = FastAPI()
client = httpx.AsyncClient()

# ✅ SEND MESSAGE FUNCTION
async def send_message(chat_id: int, text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    await client.post(url, json=payload)

# ✅ FORWARD LINK TO GOOGLE SHEET
async def forward_to_google_sheet(link: str):
    await client.post(WEB_APP_URL, data={"link": link})

# ✅ CLEAN LINK FUNCTION
def extract_link(text: str) -> str:
    for word in text.split():
        if word.startswith("http"):
            return word
    return ""

# ✅ WEBHOOK ENDPOINT
@app.post(f"/{WEBHOOK_SECRET}")
async def telegram_webhook(req: Request):
    data = await req.json()
    message = data.get("message")
    if not message:
        return {"status": "no message"}

    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]

    # ✅ Only allow specific Telegram user ID
    if user_id not in ALLOWED_USER_IDS:
        await send_message(chat_id, "⛔️ Permission denied.")
        raise HTTPException(status_code=403, detail="Unauthorized user")

    text = message.get("text", "")
    link = extract_link(text)

    if link:
        await forward_to_google_sheet(link)
        await send_message(chat_id, link)
    else:
        await send_message(chat_id, "❌ কোনো লিংক খুঁজে পাওয়া যায়নি!")

    return {"status": "ok"}
