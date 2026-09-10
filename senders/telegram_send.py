#!/usr/bin/env python3
"""
Telegram sender - Real implementation ported from AutoClaw.
Expected interface: send(content: str, idempotency_key: str, image_path: str = None) -> None
"""
import os
import json
import pathlib
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path
from dotenv import load_dotenv

# Load .env from repo root
REPO_ROOT = Path(__file__).parent.parent
load_dotenv(str(REPO_ROOT / ".env"))

# Read from environment - NO HARDCODED TOKENS
TELEGRAM_BOT_TOKEN_1 = os.environ.get("TELEGRAM_BOT_TOKEN_1")
TELEGRAM_BOT_TOKEN_2 = os.environ.get("TELEGRAM_BOT_TOKEN_2")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "@CompassEnglishAcademy")


def get_active_token() -> str:
    """Get the first available valid token."""
    if TELEGRAM_BOT_TOKEN_2 and len(TELEGRAM_BOT_TOKEN_2) > 20:
        return TELEGRAM_BOT_TOKEN_2
    if TELEGRAM_BOT_TOKEN_1 and len(TELEGRAM_BOT_TOKEN_1) > 20:
        return TELEGRAM_BOT_TOKEN_1
    raise RuntimeError("No valid TELEGRAM_BOT_TOKEN found (checked _1 and _2)")


def api_url(token: str, method: str) -> str:
    return f"https://api.telegram.org/bot{token}/{method}"


def api_call(token: str, method: str, data: dict = None) -> dict:
    url = api_url(token, method)
    if data:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
    else:
        req = urllib.request.Request(url)

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        return {"ok": False, "error_code": e.code, "description": body}


def api_post_multipart(token: str, method: str, data: dict, files: dict) -> dict:
    url = api_url(token, method)
    boundary = "----TelegramSenderBoundary"
    body = bytearray()
    for key, val in data.items():
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode())
        body.extend(f"{val}\r\n".encode())
    for field_name, filepath in files.items():
        filename = pathlib.Path(filepath).name
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'.encode())
        body.extend(b"Content-Type: application/octet-stream\r\n\r\n")
        body.extend(pathlib.Path(filepath).read_bytes())
        body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode())
    req = urllib.request.Request(
        url,
        data=bytes(body),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body_err = e.read().decode(errors="replace")
        return {"ok": False, "error_code": e.code, "description": body_err}


def send_photo(image_path: str, caption: str = None) -> dict:
    """Send a photo with optional caption via sendPhoto."""
    token = get_active_token()
    data = {"chat_id": TELEGRAM_CHAT_ID}
    if caption:
        data["caption"] = caption
        data["parse_mode"] = "HTML"
    result = api_post_multipart(token, "sendPhoto", data, files={"photo": image_path})
    if not result.get("ok"):
        raise RuntimeError(f"Telegram sendPhoto failed: {result.get('description', result)}")
    return result


def send(content: str, idempotency_key: str, image_path: str = None) -> None:
    """Main interface expected by dispatch_due.py"""
    token = get_active_token()

    if image_path:
        send_photo(image_path, caption=content)
        print(f"OK - sent photo+caption to Telegram (idempotency: {idempotency_key})")
        return

    result = api_call(token, "sendMessage", {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": content,
        "parse_mode": "HTML"
    })

    if not result.get("ok"):
        raise RuntimeError(f"Telegram send failed: {result.get('description', result)}")

    print(f"OK - sent to Telegram (idempotency: {idempotency_key})")


def verify_bot(token: str) -> dict:
    """Verify bot token and get bot info."""
    return api_call(token, "getMe")


def verify_chat(token: str) -> dict:
    """Verify chat access and bot admin status."""
    me = api_call(token, "getMe")["result"]
    ch = api_call(token, "getChat", {"chat_id": TELEGRAM_CHAT_ID})
    r = ch.get("result", {})
    m = api_call(token, "getChatMember", {"chat_id": TELEGRAM_CHAT_ID, "user_id": me["id"]})
    res = m.get("result", {})
    return {
        "bot": me,
        "chat": r,
        "member_status": res.get("status"),
        "permissions": res.get("permissions") or res.get("rights") or {}
    }


if __name__ == "__main__":
    # Allow direct CLI usage for testing
    import sys
    if len(sys.argv) < 2:
        print("Usage: python telegram_send.py 'message text'")
        print("       python telegram_send.py --verify")
        print("       python telegram_send.py --photo /path/to/img.png 'caption text'")
        sys.exit(1)

    if sys.argv[1] == "--verify":
        token = get_active_token()
        print("Verifying bot...")
        bot_info = verify_bot(token)
        print(f"Bot: @{bot_info['result']['username']} (id {bot_info['result']['id']})")

        print("Verifying chat access...")
        chat_info = verify_chat(token)
        print(f"Chat: {chat_info['chat'].get('title')} (id {chat_info['chat'].get('id')})")
        print(f"Member status: {chat_info['member_status']}")
        print(f"Permissions: {chat_info['permissions']}")
    elif sys.argv[1] == "--photo":
        img = sys.argv[2]
        caption = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else None
        send(caption or "", idempotency_key=f"cli-{os.urandom(4).hex()}", image_path=img)
    else:
        text = " ".join(sys.argv[1:])
        send(text, idempotency_key=f"cli-{os.urandom(4).hex()}")
