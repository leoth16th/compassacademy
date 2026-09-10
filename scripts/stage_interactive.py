#!/usr/bin/env python3
"""
Interactive staging. Asks questions one at a time, validates each answer
before moving on, shows a final summary, asks for confirmation, then stages
the post. No flags to remember. Always posts to BOTH telegram and bale.
Text is pasted directly. Image is found by filename in ~/Downloads.
"""
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
STAGE_POST = SCRIPT_DIR / "stage_post.py"
DOWNLOADS = Path.home() / "Downloads"


def validate_date(v: str):
    try:
        datetime.strptime(v, "%Y-%m-%d")
    except ValueError:
        return "format must be YYYY-MM-DD, e.g. 2026-09-12"
    return None


def find_image(name_fragment: str) -> Path | None:
    """Search ~/Downloads for a file whose name contains the fragment
    (case-insensitive). Returns newest match if multiple."""
    if not DOWNLOADS.is_dir():
        return None
    matches = [
        p for p in DOWNLOADS.iterdir()
        if p.is_file() and name_fragment.lower() in p.name.lower()
    ]
    if not matches:
        return None
    return max(matches, key=lambda p: p.stat().st_mtime)


def get_multiline_text() -> str:
    print("Paste the post text below. When done, type a lone '.' on its own line and press Enter:")
    lines = []
    while True:
        line = input()
        if line.strip() == ".":
            break
        lines.append(line)
    return "\n".join(lines).strip()


def main():
    print("=== Compass: stage a post (goes to BOTH Telegram and Bale) ===\n")

    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    while True:
        date = input(f"Post date (YYYY-MM-DD) [{tomorrow}]: ").strip() or tomorrow
        err = validate_date(date)
        if not err:
            break
        print(f"  -> {err}")

    text = get_multiline_text()
    while not text:
        print("  -> text can't be empty")
        text = get_multiline_text()

    image_path = None
    has_image = input("\nDoes this post have a photo? (y/n) [y]: ").strip().lower()
    if has_image != "n":
        while True:
            frag = input("Image filename (or part of it — I'll search ~/Downloads): ").strip()
            if not frag:
                print("  -> can't be empty")
                continue
            found = find_image(frag)
            if found:
                confirm_img = input(f"  Found: {found.name} — use this? (y/n) [y]: ").strip().lower()
                if confirm_img != "n":
                    image_path = found
                    break
                continue
            direct = Path(frag).expanduser()
            if direct.is_file():
                image_path = direct
                break
            print(f"  -> no match in ~/Downloads for '{frag}', and not a direct path either")

    pillar = input("\nPillar (collocation / markup / diagnostic / leave blank): ").strip()

    # write text to a temp file for stage_post.py
    tmp_text = Path(tempfile.mkstemp(suffix=".txt")[1])
    tmp_text.write_text(text, encoding="utf-8")

    print("\n--- About to stage (Telegram + Bale) ---")
    print(f"Send on  : {date} at 08:00 Tehran (GitHub Actions daily run)")
    print(f"Text     :\n{text}\n")
    print(f"Image    : {image_path or '(none)'}")
    print(f"Pillar   : {pillar or '(none)'}")
    print("-----------------------------------------\n")

    confirm = input("Confirm and stage this? (y/n): ").strip().lower()
    if confirm != "y":
        print("Cancelled. Nothing staged.")
        sys.exit(0)

    any_fail = False
    for platform in ("telegram", "bale"):
        cmd = [
            sys.executable, str(STAGE_POST),
            "--platform", platform,
            "--date", date,
            "--text-file", str(tmp_text),
        ]
        if image_path:
            cmd += ["--image", str(image_path)]
        if pillar:
            cmd += ["--pillar", pillar]

        result = subprocess.run(cmd, capture_output=True, text=True)
        print(f"[{platform}]")
        print(result.stdout)
        if result.returncode != 0:
            print(f"STAGING FAILED for {platform}:")
            print(result.stderr)
            any_fail = True

    if any_fail:
        sys.exit(1)

    print("Staged successfully for both platforms.\n")

    push_now = input("Push to GitHub now so it actually sends? (y/n) [y]: ").strip().lower()
    if push_now == "n":
        print("Not pushed. Nothing will send until you run: ./daily.sh push")
        sys.exit(0)

    push_result = subprocess.run(
        [str(SCRIPT_DIR / "daily.sh"), "push"],
        capture_output=True, text=True
    )
    print(push_result.stdout)
    if push_result.returncode != 0:
        print("PUSH FAILED:")
        print(push_result.stderr)
        sys.exit(1)

    print(f"DONE. Posts will send on {date} at 08:00 Tehran automatically.")


if __name__ == "__main__":
    main()
