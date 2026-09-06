#!/usr/bin/env python3
"""
Mechanical dispatcher. Reads control.db for 'staged' automated items,
sends anything due and not yet posted, marks it posted. Runs unattended
on GitHub Actions (or any always-on host) so sends happen even if Mike's
machine is off. Never generates content — content_path already holds the
finished text Claude wrote.
"""
import argparse
import sqlite3
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import telegram_send  # TODO: port Mike's existing telegram sender here
import bale_send       # TODO: port Mike's existing bale sender here
# import hugo_publish  # wire in when the FTP -> git blog migration happens

SENDERS = {
    "telegram": telegram_send.send,
    "bale": bale_send.send,
}


def due_items(db_path: str, tz: str) -> list[dict]:
    now = datetime.now(ZoneInfo(tz))
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT * FROM content_items WHERE state='staged' AND mode='automated'"
    ).fetchall()
    con.close()
    due = []
    for r in rows:
        scheduled = datetime.fromisoformat(
            f"{r['post_date']}T{r['post_time']}"
        ).replace(tzinfo=ZoneInfo(tz))
        if scheduled <= now:
            due.append(dict(r))
    return due


def already_sent(db_path: str, idempotency_key: str) -> bool:
    """Check if this item has already been sent (across DB copies)."""
    con = sqlite3.connect(db_path)
    row = con.execute(
        "SELECT 1 FROM sent_log WHERE idempotency_key = ?",
        (idempotency_key,)
    ).fetchone()
    con.close()
    return row is not None


def mark_sent(db_path: str, idempotency_key: str) -> None:
    """Record that this item has been sent (idempotent - PK prevents dups)."""
    con = sqlite3.connect(db_path)
    con.execute(
        "INSERT OR IGNORE INTO sent_log (idempotency_key, sent_at) VALUES (?, ?)",
        (idempotency_key, datetime.utcnow().isoformat()),
    )
    con.commit()
    con.close()


def mark_posted(db_path: str, item_id: str) -> None:
    con = sqlite3.connect(db_path)
    con.execute(
        "UPDATE content_items SET state='posted', posted_at=? WHERE id=?",
        (datetime.utcnow().isoformat(), item_id),
    )
    con.commit()
    con.close()


def main(tz: str, db_path: str) -> None:
    for item in due_items(db_path, tz):
        ik = item["idempotency_key"]
        if already_sent(db_path, ik):
            print(f"⏭ SKIPPED duplicate (sent_log): {item['id']} -> {item['platform']}")
            # Still mark as posted in content_items if not already
            mark_posted(db_path, item["id"])
            continue

        sender = SENDERS.get(item["platform"])
        if sender is None:
            print(f"no sender wired for platform={item['platform']}, skipping")
            continue

        content = Path(item["content_path"]).read_text(encoding="utf-8")
        try:
            sender(content=content, idempotency_key=ik)
            mark_sent(db_path, ik)
            mark_posted(db_path, item["id"])
            print(f"✓ posted {item['id']} to {item['platform']}")
        except Exception as e:
            print(f"✗ FAILED to post {item['id']} to {item['platform']}: {e}")
            raise


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--tz", default="Asia/Tehran")
    p.add_argument("--db", default="control.db")
    args = p.parse_args()
    main(tz=args.tz, db_path=args.db)
