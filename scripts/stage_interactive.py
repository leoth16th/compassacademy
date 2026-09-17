#!/usr/bin/env python3
"""
Interactive staging. Asks questions one at a time, validates each answer
before moving on, shows a final summary, asks for confirmation, then stages
the post. No flags to remember. Always posts to BOTH telegram and bale.
Text is pasted directly. Image is found by filename in ~/Downloads.
"""
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
STAGE_POST = SCRIPT_DIR / "stage_post.py"
PICK_IDEA = SCRIPT_DIR / "pick_idea.py"
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


def get_idea(pillar: str):
    """Call pick_idea.py, return parsed JSON dict or None on failure."""
    cmd = [sys.executable, str(PICK_IDEA)]
    if pillar:
        cmd.append(pillar)
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        data = json.loads(result.stdout)
    except (json.JSONDecodeError, ValueError):
        return None
    if data.get("status") != "ok":
        return None
    return data["picked"]


def main():
    print("=== Compass: stage a post (goes to BOTH Telegram and Bale) ===\n")

    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    while True:
        date = input(f"Post date (YYYY-MM-DD) [{tomorrow}]: ").strip() or tomorrow
        err = validate_date(date)
        if not err:
            break
        print(f"  -> {err}")

    pillar_for_idea = input("\nPillar for today's idea (saturday=test_info / monday=collocation / wednesday=student_mistake / blank = any): ").strip()
    idea = get_idea(pillar_for_idea)
    if idea:
        print("\n--- Today's idea (already marked used) ---")
        print(f"id       : {idea['id']}")
        print(f"pillar   : {idea['pillar']}")
        if idea.get("ready_made_content"):
            print(f"source   : {idea['ready_made_path']}")
            print("-------------------------------------------")
            print(idea["ready_made_content"])
        else:
            print(f"wrong    : {idea['example_wrong']}")
            print(f"correct  : {idea['example_correct']}")
            print(f"why      : {idea['explanation']}")
        print("-------------------------------------------")
        print("Copy this into your web AI to draft the post.\n")
    else:
        print("\n  -> no unused idea found (or pick_idea.py failed) — draft freely.\n")

    carousel_sh = SCRIPT_DIR.parent.parent / "ig-carousel-builder" / "run-carousel.sh"
    if carousel_sh.is_file():
        subprocess.Popen(["bash", str(carousel_sh)],
                          cwd=str(carousel_sh.parent),
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("  -> launching builder at http://localhost:4000")
    else:
        print(f"  -> not found: {carousel_sh}")

    # Profile 3 = mycompassenglishacademy@gmail.com (Compass)
    # Profile 1 = leo16th1989@gmail.com (Leo)
    subprocess.Popen(
        ["google-chrome", "--profile-directory=Profile 3", "https://www.instagram.com/"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    print("  -> opening Instagram in Chrome (Compass profile)")

    subprocess.Popen(
        ["google-chrome", "--profile-directory=Profile 1", "https://chat.openai.com/"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    print("  -> opening ChatGPT in Chrome (Leo profile)")

    subprocess.Popen(
        ["google-chrome", "--profile-directory=Profile 1", "https://claude.ai/"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    print("  -> opening Claude in Chrome (Leo profile)")

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

    pillar = input("\nPillar (test_info / collocation / student_mistake / leave blank): ").strip()

    # write text to a temp file for stage_post.py
    tmp_text = Path(tempfile.mkstemp(suffix=".txt")[1])
    tmp_text.write_text(text, encoding="utf-8")

    print("\n--- About to stage (Telegram + Bale) ---")
    print(f"Send on  : {date} at 08:00 Tehran (GitHub Actions daily run)")
    print(f"Text     :\n{text}\n")
    print(f"Image    : {image_path or '(none)'}")
    print(f"Pillar   : {pillar or '(none)'}")
    print("-----------------------------------------\n")

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
