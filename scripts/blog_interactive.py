#!/usr/bin/env python3
"""
Interactive wrapper around publisher-v2/publish.py. Asks whether there's a
blog post today. If yes, finds the EN/FA files (search content dirs by
filename fragment, same trick as image search) and runs publish.py in
split mode. If no, does nothing.
"""
import subprocess
import sys
from pathlib import Path

SITE_ROOT = Path("/home/mike/compass-system/website/hugo-site-2-main")
PUBLISHER = SITE_ROOT / "publisher-v2" / "publish.py"
EN_DIR = SITE_ROOT / "content" / "en" / "blog"
FA_DIR = SITE_ROOT / "content" / "fa" / "blog"


def find_file(directory: Path, fragment: str) -> Path | None:
    if not directory.is_dir():
        return None
    matches = [
        p for p in directory.iterdir()
        if p.is_file() and fragment.lower() in p.name.lower()
    ]
    if not matches:
        return None
    return max(matches, key=lambda p: p.stat().st_mtime)


def pick_file(directory: Path, label: str) -> Path:
    while True:
        frag = input(f"{label} filename (or part of it, e.g. 'post-15'): ").strip()
        if not frag:
            print("  -> can't be empty")
            continue
        found = find_file(directory, frag)
        if found:
            confirm = input(f"  Found: {found.name} — use this? (y/n) [y]: ").strip().lower()
            if confirm != "n":
                return found
            continue
        direct = Path(frag).expanduser()
        if direct.is_file():
            return direct
        print(f"  -> no match in {directory} for '{frag}'")


def main():
    has_post = input("Blog post today? (y/n) [n]: ").strip().lower()
    if has_post != "y":
        print("No blog post. Skipping.")
        sys.exit(0)

    print(f"\nSearching in:\n  EN: {EN_DIR}\n  FA: {FA_DIR}\n")
    en_file = pick_file(EN_DIR, "EN post")
    fa_file = pick_file(FA_DIR, "FA post")

    print(f"\nEN: {en_file}")
    print(f"FA: {fa_file}")
    confirm = input("\nRun publisher (build + git commit, will ask before live FTP deploy)? (y/n) [y]: ").strip().lower()
    if confirm == "n":
        print("Cancelled.")
        sys.exit(0)

    # Run interactively so the publisher's own deploy-confirmation prompt
    # still works — don't capture stdio here.
    result = subprocess.run(
        [sys.executable, str(PUBLISHER), "--en-file", str(en_file), "--fa-file", str(fa_file)],
        cwd=str(PUBLISHER.parent),
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
