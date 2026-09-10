#!/usr/bin/env python3
"""
Stage a finished post (text + optional photo) into control.db so the daily
GitHub Actions run picks it up and sends it. No AI. No guessing.

You already: got an idea, wrote the content, made the pic if needed.
This script is the ONLY step between "content is ready" and "it will be
sent automatically". It does not push to git -- daily.sh does that after.

Usage:
  python3 stage_post.py --platform telegram --date 2026-09-12 \
      --text-file /path/to/caption.txt \
      --image /path/to/pic.png \
      --pillar collocation

  python3 stage_post.py --platform bale --date 2026-09-12 \
      --text-file /path/to/caption.txt
"""
import argparse
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path("/home/mike/compass-system/compassacademy")
CONTROL_DB = ROOT / "control.db"
POSTING_DIR = ROOT / "posting"

VALID_PLATFORMS = {"telegram", "bale"}  # only ones dispatch_due.py can actually send


def week_id_for(date: datetime) -> str:
    y, w, _ = date.isocalendar()
    return f"{y}-W{w:02d}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--platform", required=True, choices=sorted(VALID_PLATFORMS))
    ap.add_argument("--date", required=True, help="YYYY-MM-DD, when it should post")
    ap.add_argument("--text-file", required=True, help="path to caption/post text file")
    ap.add_argument("--image", default=None, help="optional path to photo")
    ap.add_argument("--pillar", default=None)
    ap.add_argument("--time", default="09:00")
    args = ap.parse_args()

    text_src = Path(args.text_file)
    if not text_src.is_file():
        print(f"FAIL: text file not found: {text_src}", file=sys.stderr)
        sys.exit(1)

    try:
        post_date = datetime.strptime(args.date, "%Y-%m-%d")
    except ValueError:
        print(f"FAIL: --date must be YYYY-MM-DD, got {args.date}", file=sys.stderr)
        sys.exit(1)

    week_id = week_id_for(post_date)

    # Copy content into posting/ so it's a stable path tracked in the repo,
    # not whatever tmp/Downloads path you happened to type.
    POSTING_DIR.mkdir(parents=True, exist_ok=True)
    slug = f"{args.date}-{args.platform}" + (f"-{args.pillar}" if args.pillar else "")
    dest_text = POSTING_DIR / f"{slug}.txt"
    shutil.copyfile(text_src, dest_text)

    dest_image = None
    if args.image:
        img_src = Path(args.image)
        if not img_src.is_file():
            print(f"FAIL: image not found: {img_src}", file=sys.stderr)
            sys.exit(1)
        dest_image = POSTING_DIR / f"{slug}{img_src.suffix}"
        shutil.copyfile(img_src, dest_image)

    item_id = f"{week_id}-{args.platform}-{slug}"
    idem = f"{week_id}:{args.platform}:{args.date}"

    conn = sqlite3.connect(CONTROL_DB)
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO cycles (week_id) VALUES (?)", (week_id,)
    )
    cur.execute(
        """
        INSERT OR REPLACE INTO content_items
            (id, week_id, platform, pillar, post_date, post_time, mode,
             content_path, idempotency_key, state, image_path)
        VALUES (?, ?, ?, ?, ?, ?, 'automated', ?, ?, 'staged', ?)
        """,
        (
            item_id, week_id, args.platform, args.pillar, args.date, args.time,
            str(dest_text), idem, str(dest_image) if dest_image else None,
        ),
    )
    conn.commit()
    conn.close()

    print(f"OK staged {item_id}")
    print(f"  text:  {dest_text}")
    if dest_image:
        print(f"  image: {dest_image}")
    print(f"  will send on {args.date} via GitHub Actions daily run")
    print(f"  NEXT: run ./daily.sh push   to commit + push this to GitHub")


if __name__ == "__main__":
    main()
