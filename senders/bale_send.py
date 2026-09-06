#!/usr/bin/env python3
"""
Bale sender - Real implementation ported from AutoClaw.
Expected interface: send(content: str, idempotency_key: str) -> None
"""
import os
import json
import urllib.request
import urllib.error
import urllib.parse
import pathlib
from pathlib import Path
from dotenv import load_dotenv

# Load .env from repo root
REPO_ROOT = Path(__file__).parent.parent
load_dotenv(str(REPO_ROOT / ".env"))

BALE_API = "https://tapi.bale.ai"

# Read from environment - NO HARDCODED TOKENS
TOKEN = os.environ.get("BALE_BOT_TOKEN")
CHAT_ID = os.environ.get("BALE_CHAT_ID", "@compassacademy")


def api_url(method):
    return f"{BALE_API}/bot{TOKEN}/{method}"


def api_post(method, data, files=None):
    if files:
        boundary = "----BaleSenderBoundary"
        body = bytearray()
        for key, val in data.items():
            body.extend(f"--{boundary}\r\n".encode())
            body.extend(f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode())
            body.extend(f"{val}\r\n".encode())
        for field_name, filepath in files.items():
            filename = pathlib.Path(filepath).name
            body.extend(f"--{boundary}\r\n".encode())
            body.extend(f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'.encode())
            body.extend("Content-Type: application/octet-stream\r\n\r\n".encode())
            body.extend(pathlib.Path(filepath).read_bytes())
            body.extend(b"\r\n")
        body.extend(f"--{boundary}--\r\n".encode())
        req = urllib.request.Request(
            api_url(method),
            data=bytes(body),
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        )
    else:
        req = urllib.request.Request(
            api_url(method),
            data=urllib.parse.urlencode(data).encode(),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        return {"ok": False, "error_code": e.code, "description": body}


def send_text(text):
    return api_post("sendMessage", {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"})


def send_photo(image_path, caption=None):
    data = {"chat_id": CHAT_ID}
    if caption:
        data["caption"] = caption
        data["parse_mode"] = "HTML"
    return api_post("sendPhoto", data, files={"photo": image_path})


def send(content: str, idempotency_key: str) -> None:
    """Main interface expected by dispatch_due.py"""
    if not TOKEN or len(TOKEN) < 20:
        raise RuntimeError("BALE_BOT_TOKEN not set or too short")
    if not CHAT_ID:
        raise RuntimeError("BALE_CHAT_ID not set")

    # Check if content references an image (simple heuristic: starts with IMAGE: or similar)
    # For now, send as text. Image support can be added if needed.
    result = send_text(content)

    if not result.get("ok"):
        raise RuntimeError(f"Bale send failed: {result.get('description', result)}")

    print(f"OK - sent to Bale (idempotency: {idempotency_key})")


if __name__ == "__main__":
    # Allow direct CLI usage for testing
    import sys
    if len(sys.argv) < 2:
        print("Usage: python bale_send.py 'message text'")
        sys.exit(1)
    text = " ".join(sys.argv[1:])
    send(text, idempotency_key=f"cli-{os.urandom(4).hex()}")