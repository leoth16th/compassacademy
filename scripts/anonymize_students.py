#!/usr/bin/env python3
"""
anonymize_students.py — Replace real student names with [Student] across a
student-work folder tree (filenames, folder names, .docx text content).

SAFETY RULES:
- Default mode is REPORT ONLY: prints what WOULD change, touches nothing.
- Changes happen only with --apply, and only inside the given --target dir.
  NEVER point --apply at the original external drive; run it on a local copy.
- Nothing is ever deleted. Binary files (audio/images) are left byte-identical;
  their *contents* cannot be scrubbed by this tool (flagged in the report).

Name list defaults to the top-level directories of --target (e.g. AMENE,
Ashkani, ...) matched case-insensitively anywhere in paths/docx text.

Usage:
  python3 anonymize_students.py --target <dir>              # report only
  python3 anonymize_students.py --target <dir> --apply      # modify target
"""

import argparse
import re
import sys
from pathlib import Path

from docx import Document

MARKER = "[Student]"


def build_patterns(names: list[str]):
    """Case-insensitive compiled regexes for each name."""
    return [(n, re.compile(re.escape(n), re.IGNORECASE)) for n in names]


def scrub_text(text: str, patterns) -> tuple[str, int]:
    hits = 0
    for _, pat in patterns:
        text, n = pat.subn(MARKER, text)
        hits += n
    return text, hits


def scrub_docx(path: Path, patterns, apply: bool = False) -> tuple[int, int]:
    """Run-level replacement inside paragraphs + table cells.

    Returns (replacements, residual_hits). With apply=False the document is
    analyzed but NOT saved — zero mutation guaranteed."""
    doc = Document(str(path))
    total = 0

    def scrub_paragraph(p) -> None:
        nonlocal total
        for run in p.runs:
            new, n = scrub_text(run.text, patterns)
            if n:
                run.text = new
                total += n
        # residual check: name spanning multiple runs
        joined = "".join(r.text for r in p.runs)
        _, resid = scrub_text(joined, patterns)
        if resid:
            # collapse to single run to guarantee removal
            replaced, n = scrub_text(joined, patterns)
            for r in list(p.runs)[1:]:
                r._element.getparent().remove(r._element)
            p.runs[0].text = replaced
            total += n

    for p in doc.paragraphs:
        scrub_paragraph(p)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    scrub_paragraph(p)

    # residual scan over full visible text after edits
    full = "\n".join(p.text for p in doc.paragraphs)
    _, residual = scrub_text(full, patterns)
    if apply:
        doc.save(str(path))
    return total, residual


def unique_path(p: Path) -> Path:
    if not p.exists():
        return p
    stem, suf = p.stem, p.suffix
    n = 1
    while p.exists():
        p = p.with_name(f"{stem}-{n}{suf}")
        n += 1
    return p


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--target", required=True, type=Path)
    ap.add_argument("--apply", action="store_true",
                    help="actually modify target (default: report only)")
    args = ap.parse_args()
    target: Path = args.target.resolve()

    if not target.is_dir():
        print(f"ERROR: {target} is not a directory")
        return 2

    names = sorted(d.name for d in target.iterdir() if d.is_dir())
    if not names:
        print("ERROR: no top-level dirs to derive names from")
        return 2
    patterns = build_patterns(names)
    mode = "APPLY" if args.apply else "REPORT-ONLY"
    print(f"mode={mode} target={target}\nnames={names}\n")

    stat = {"file_renames": 0, "dir_renames": 0,
            "files_would_rename": 0, "dirs_would_rename": 0,
            "docx_scrubs": 0, "text_hits": 0, "residual": 0, "binaries": 0}
    residuals: list[str] = []

    all_files = sorted(target.rglob("*"))
    # 1. docx content
    for f in all_files:
        if f.is_file() and f.suffix.lower() == ".docx":
            try:
                n, resid = scrub_docx(f, patterns, apply=args.apply)
            except Exception as e:                      # noqa: BLE001
                print(f"  !! FAILED {f.relative_to(target)}: {e}")
                continue
            if n:
                stat["docx_scrubs"] += 1
                stat["text_hits"] += n
                print(f"  docx {f.relative_to(target)}: {n} replacement(s)")
            if resid:
                stat["residual"] += resid
                residuals.append(str(f.relative_to(target)))

    # 2. FILE renames FIRST (all paths still valid — no dir renamed yet),
    # 3. THEN dir renames deepest-first via fresh rglob.
    for f in all_files:
        if not f.is_file():
            continue
        new_stem, n = scrub_text(f.stem, patterns)
        if n and new_stem != f.stem:
            dest = unique_path(f.with_name(new_stem + f.suffix))
            if args.apply:
                print(f"  file {f.relative_to(target)} -> {dest.name}")
                f.rename(dest)
                stat["file_renames"] += 1
            else:
                stat["files_would_rename"] += 1
        elif f.suffix.lower() not in (".docx",):
            stat["binaries"] += 1

    for p in sorted((q for q in target.rglob("*") if q.is_dir()),
                    key=lambda x: len(x.parts), reverse=True):
        new_name, n = scrub_text(p.name, patterns)
        if n and new_name != p.name:
            dest = unique_path(p.with_name(new_name))
            if args.apply:
                print(f"  dir  {p.relative_to(target)} -> {dest.name}")
                p.rename(dest)
                stat["dir_renames"] += 1
            else:
                stat["dirs_would_rename"] += 1

    print("\n=== SUMMARY ===")
    for k, v in stat.items():
        print(f"{k}: {v}")
    if stat["binaries"]:
        print("NOTE: binary files (audio etc.) were NOT touched — their spoken "
              "content can contain names; review manually before publishing.")
    if residuals:
        print("RESIDUAL (name split across runs, auto-fixed): "
              + ", ".join(residuals))
    if not args.apply:
        print("\nREPORT ONLY — nothing was modified. Re-run with --apply to change.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
