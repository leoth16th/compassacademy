#!/usr/bin/env python3
"""
Delete duplicate Telegram messages from @CompassEnglishAcademy channel.
Uses TELEGRAM_BOT_TOKEN_2 (channel_contentbot) which is admin.
Run with: TELEGRAM_BOT_TOKEN_2="your_token" python3 delete_telegram_duplicates.py
"""
import os
import asyncio
import aiohttp

TELEGRAM_BOT_TOKEN_2 = os.environ.get("TELEGRAM_BOT_TOKEN_2")
CHANNEL_USERNAME = "@CompassEnglishAcademy"

if not TELEGRAM_BOT_TOKEN_2:
    print("ERROR: TELEGRAM_BOT_TOKEN_2 not set in environment")
    print("Run: TELEGRAM_BOT_TOKEN_2='your_token' python3 delete_telegram_duplicates.py")
    exit(1)

async def delete_message(session, chat_id, message_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN_2}/deleteMessage"
    payload = {"chat_id": chat_id, "message_id": message_id}
    async with session.post(url, json=payload) as resp:
        result = await resp.json()
        return result

async def get_chat_id(session):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN_2}/getChat"
    payload = {"chat_id": CHANNEL_USERNAME}
    async with session.post(url, json=payload) as resp:
        result = await resp.json()
        if result.get("ok"):
            return result["result"]["id"]
        else:
            print(f"Failed to get chat ID: {result}")
            return None

async def main():
    # Based on the timeline:
    # - Message 22: 16:15 (ORIGINAL - KEEP)
    # - Messages 23-28: duplicates from the 3 failed runs (DELETE) = 6 duplicates
    duplicate_ids = list(range(23, 29))  # 23, 24, 25, 26, 27, 28
    
    async with aiohttp.ClientSession() as session:
        chat_id = await get_chat_id(session)
        if not chat_id:
            return
        
        print(f"Channel chat_id: {chat_id}")
        print(f"Will delete message IDs: {duplicate_ids}")
        
        for msg_id in duplicate_ids:
            result = await delete_message(session, chat_id, msg_id)
            if result.get("ok"):
                print(f"✅ Deleted message {msg_id}")
            else:
                print(f"❌ Failed to delete {msg_id}: {result}")

if __name__ == "__main__":
    asyncio.run(main())
