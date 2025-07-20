from fastapi import FastAPI, Request, HTTPException
import httpx
import os

app = FastAPI()

BOT_TOKEN = "6897920120:AAG---REPLACE-YOUR-TOKEN---g"  # ← Put your full Bot Token
WEBHOOK_SECRET = "1fffa43"  # ← Your Webhook Path
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwoq2rokXRRIwFr60OKqJI8MhtvVpIepxCKZ9A-n7CV_COxQIdsMiKQ5EoMhPIkn7K3bw/exec"

ALLOWED_USER_ID = 1414414216  # ← Only you can message the bot

@app.post(f"/{WEBHOOK_SECRET}")
async def telegram_webhook(req: Request):
    payload = await req.json()

    # Extract message
    message = payload.get("message")
    if not message:
        return {"ok": True}

    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    text = message.get("text", "")

    # Only allow specific user
    if user_id != ALLOWED_USER_ID:
        await send_message(chat_id, "❌ Permission denied.")
        return {"ok": True}

    # Extract only link from text
    link = extract_link(text)
    if not link:
        await send_message(chat_id, "❌ কোনো লিংক পাওয়া যায়নি।")
        return {"ok": True}

    # Send to Web App
    try:
        async with httpx.AsyncClient() as client:
            await client.post(WEB_APP_URL, data={"link": link})
        await send_message(chat_id, f"✅ লিংক যোগ হয়েছে:\n{link}")
    except Exception as e:
        await send_message(chat_id, f"❌ সমস্যা হয়েছে:\n{str(e)}")

    return {"ok": True}

def extract_link(text):
    words = text.split()
    for word in words:
        if word.startswith("http://") or word.startswith("https://"):
            return word
    return None

async def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)
