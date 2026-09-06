#!/usr/bin/env python3
"""
download_monitor.py — Carousel PNG download organizer.

Watches ~/Downloads/ for carousel export PNGs (pattern: *-slide-*.png,
matching ig-carousel-builder's export naming `{handle}-slide-{N}.png`)
and moves them into the active cycle's instagram folder:

    <CANONICAL_ROOT>/cycle/<week_id>/instagram/

Rules:
- NEVER overwrites: duplicate names get a numeric suffix (-1, -2, ...).
- Only picks up the active (status='open') cycle from control.db.
  If no open cycle exists, files are LEFT in ~/Downloads (logged as skipped).
- Never deletes anything. Moves are logged to monitor.log next to this script.

Usage:
  python3 download_monitor.py --once   # single pass (cron-friendly)
  python3 download_monitor.py --watch  # poll every 10s until Ctrl-C
"""

import argparse
import shutil
import sqlite3
import time
from pathlib import Path

HOME = Path.home()
DOWNLOADS = HOME / "Downloads"
CANONICAL_ROOT = HOME / "compass-system" / "compassacademy"
CONTROL_DB = CANONICAL_ROOT / "control.db"
LOG_FILE = Path(__file__).resolve().parent / "monitor.log"
PATTERN = "*-slide-*.png"  # matches {handle}-slide-{N}.png from CarouselPreview.jsx
POLL_SECONDS = 10


def log(msg: str) -> None:
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line)
    with LOG_FILE.open("a") as f:
        f.write(line + "\n")


def get_active_week(db_path: Path) -> str | None:
    """Return the open cycle week_id, else None."""
    con = sqlite3.connect(db_path)
    try:
        row = con.execute(
            "SELECT week_id FROM cycles WHERE status='open' ORDER BY week_id DESC LIMIT 1"
        ).fetchone()
    finally:
        con.close()
    return row[0] if row else None


def unique_target(folder: Path, name: str) -> Path:
    """Return a path in folder that doesn't exist yet (suffix -1, -2 ...)."""
    candidate = folder / name
    stem, suffix = Path(name).stem, Path(name).suffix
    n = 1
    while candidate.exists():
        candidate = folder / f"{stem}-{n}{suffix}"
        n += 1
    return candidate


def process_once() -> int:
    if not CONTROL_DB.exists():
        log(f"SKIP no control.db at {CONTROL_DB}")
        return 0
    week = get_active_week(CONTROL_DB)
    if not week:
        log("SKIP no open cycle in control.db — leaving Downloads untouched")
        return 0
    dest_dir = CANONICAL_ROOT / "cycle" / week / "instagram"
    moved = 0
    for src in sorted(DOWNLOADS.glob(PATTERN)):
        if not src.is_file():
            continue
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = unique_target(dest_dir, src.name)
        shutil.move(str(src), str(dest))
        log(f"MOVED {src.name} -> cycle/{week}/instagram/{dest.name}")
        moved += 1
    return moved


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--once", action="store_true", help="single pass")
    g.add_argument("--watch", action="store_true", help="poll forever")
    args = ap.parse_args()

    DOWNLOADS.mkdir(exist_ok=True)
    if args.watch:
        log(f"WATCH started: {DOWNLOADS} ({PATTERN}) -> active cycle instagram/")
        while True:
            process_once()
            time.sleep(POLL_SECONDS)
    else:
        n = process_once()
        log(f"DONE single pass: {n} file(s) moved")


if __name__ == "__main__":
    main()
