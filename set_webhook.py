"""
Run this ONCE after deploy to register the webhook with Telegram.
Usage: python set_webhook.py
"""
import os, requests
from dotenv import load_dotenv

load_dotenv()

TOKEN     = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")

url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
r   = requests.post(url, json={"url": f"{WEBAPP_URL}/webhook"})
print(r.json())
