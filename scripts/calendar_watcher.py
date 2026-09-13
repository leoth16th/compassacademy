#!/usr/bin/env python3
"""
calendar_watcher.py - Daily empty-slot guard for the Compass content system.

Checks current + next ISO week's three locked pillar slots (Sat/Mon/Wed).
If any slot has NO content_items row in control.db, sends Mike one Telegram
message listing exactly which slots are empty. If everything is filled,
sends NOTHING (silent when healthy).

Cron: 0 9 * * *  (09:00 Tehran, machine local time is +0330)
Usage: python3 scripts/calendar_watcher.py
"""
import os
import sqlite3
import sys
from datetime import date, timedelta
from pathlib import Path
from dotenv import load_dotenv

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "senders"))

# Load .env from repo root
load_dotenv(str(Path(REPO) / ".env"))

DB_PATH = os.path.join(REPO, "control.db")

# ISO weekday: Mon=0 ... Sun=6. Locked pillars:
# Saturday=5 -> test_info | Monday=0 -> collocation | Wednesday=2 -> student_mistake
SLOTS = [(0, "collocation"), (2, "student_mistake"), (5, "test_info")]


def iso_week_id(d: date) -> str:
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"


def week_dates(week_id: str):
    """Return the Mon..Sun dates of an ISO week given as YYYY-Www."""
    y, w = week_id.split("-W")
    ref = date.fromisocalendar(int(y), int(w), 1)  # Monday of that week
    return [ref + timedelta(days=i) for i in range(7)]


def find_empty_slots():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    today = date.today()
    weeks = [iso_week_id(today), iso_week_id(today + timedelta(days=7))]

    empty = []
    for wk in weeks:
        days = week_dates(wk)
        for wd, pillar in SLOTS:
            slot_date = next(d for d in days if d.weekday() == wd)
            cur.execute(
                """SELECT COUNT(*) FROM content_items
                   WHERE week_id=? AND platform IN ('telegram','bale','instagram','whatsapp')
                     AND (pillar=? OR pillar LIKE ?)""",
                (wk, pillar, f"%{pillar}%"),
            )
            count = cur.fetchone()[0]
            if count == 0:
                day_name = slot_date.strftime("%a")
                empty.append(f"  - {wk} {day_name} {slot_date.isoformat()} [{pillar}]")
    conn.close()
    return empty


def main():
    empty = find_empty_slots()
    if not empty:
        print("All Sat/Mon/Wed slots filled for current + next week. Silent.")
        return

    msg = (
        "📋 Calendar check — EMPTY pillar slots:\n"
        + "\n".join(empty)
        + "\n\nThese need drafting before cycle-intake."
    )

    # SAFETY: default TELEGRAM_CHAT_ID is the PUBLIC channel. Ops alerts must go
    # to Mike's private chat only. Refuse to send unless MIKE_CHAT_ID is set.
    mike_chat = os.environ.get("MIKE_CHAT_ID")
    if not mike_chat:
        print("SKIP: MIKE_CHAT_ID not set in .env — refusing to post ops alerts to the public channel.")
        return

    import telegram_send
    telegram_send.TELEGRAM_CHAT_ID = mike_chat  # override channel default

    from telegram_send import send
    key = f"calendar-watcher:{date.today().isoformat()}"
    send(msg, key)  # idempotency_key prevents double alerts same day
    print(f"Alert sent to Mike ({len(empty)} empty slots): {key}")


if __name__ == "__main__":
    main()
