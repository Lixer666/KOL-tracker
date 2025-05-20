# KOL-tracker Mobile Version
# Мінімальна версія для запуску на телефоні (Termux/Android)
# Потрібно: pip install telethon requests

import asyncio
from telethon import TelegramClient, events
import requests

# --- Налаштування ---
api_id = '21412253'
api_hash = '26a846f4cf5d1a873985b6b3a5fda7bf'
chat_id = 'gmgnsignals'  # username каналу або ID
BOT_TOKEN = 'gmgnsignals'
NOTIFICATION_CHAT_ID = ['7232791762', '7760875761']  # список ID для надсилання

# --- Мінімальна функція для надсилання повідомлень ---
def send_telegram_notification(message):
    for chat_id in NOTIFICATION_CHAT_ID:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {'chat_id': chat_id, 'text': message, 'parse_mode': 'HTML'}
            requests.post(url, json=payload)
        except Exception as e:
            print(f"Error sending to {chat_id}: {e}")

# --- Основна логіка ---
async def main():
    session_file = 'session_mobile'
    client = TelegramClient(session_file, api_id, api_hash)

    @client.on(events.NewMessage(chats=chat_id))
    async def handler(event):
        text = event.message.text or ''
        if 'KOL' in text and 'Buy' in text:
            print(f"[MOBILE] Token: {text[:60]}")
            send_telegram_notification(f"[MOBILE] Token: {text[:60]}")

    async with client:
        print("[MOBILE] Bot started. Waiting for signals...")
        await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
