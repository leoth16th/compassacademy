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
        sender = SENDERS.get(item["platform"])
        if sender is None:
            print(f"no sender wired for platform={item['platform']}, skipping")
            continue
        content = Path(item["content_path"]).read_text(encoding="utf-8")
        # idempotency_key stops a re-run from double-posting the same item
        sender(content=content, idempotency_key=item["idempotency_key"])
        mark_posted(db_path, item["id"])
        print(f"posted {item['id']} to {item['platform']}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--tz", default="Asia/Tehran")
    p.add_argument("--db", default="control.db")
    args = p.parse_args()
    main(tz=args.tz, db_path=args.db)
