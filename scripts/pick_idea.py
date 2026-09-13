#!/usr/bin/env python3
"""
Pure logic idea-picker. No LLM. No agent. Extracted from recipes/pick-idea.yaml
so it runs standalone with zero Goose/agent overhead.

Pillars: test_info (Saturday, TOEFL/IELTS exam-info posts) / collocation
(Monday) / student_mistake (Wednesday, real student errors).

Usage:
  python3 pick_idea.py                  # any unused idea
  python3 pick_idea.py collocation      # unused idea for this pillar, fallback any
  python3 pick_idea.py saturday         # same as test_info
"""
import sqlite3
import json
import sys
from pathlib import Path

DB = "/home/mike/compass-system/raw_material.db"

DAY_ALIASES = {
    "saturday": "test_info",
    "monday": "collocation",
    "wednesday": "student_mistake",
    # accept the old names too, in case something still passes them
    "diagnostic": "test_info",
    "surgical_info": "test_info",
    "markup": "student_mistake",
    "diagnostic_markup": "student_mistake",
}


def main() -> None:
    raw_pillar = sys.argv[1].strip().lower() if len(sys.argv) > 1 else ""
    pillar = DAY_ALIASES.get(raw_pillar, raw_pillar)

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    total = cur.execute("SELECT COUNT(*) FROM raw_material").fetchone()[0]
    unused_total = cur.execute("SELECT COUNT(*) FROM raw_material WHERE used=0").fetchone()[0]

    picked = None
    if pillar:
        picked = cur.execute(
            "SELECT * FROM raw_material WHERE used=0 AND pillar=? ORDER BY id LIMIT 1",
            (pillar,)
        ).fetchone()

    if picked is None:
        picked = cur.execute(
            "SELECT * FROM raw_material WHERE used=0 ORDER BY id LIMIT 1"
        ).fetchone()

    if picked is None:
        print(json.dumps({
            "status": "error",
            "detail": "No unused rows left in raw_material.db.",
            "total_rows": total,
            "rows_unused": unused_total,
            "pillar_filter": pillar,
        }, ensure_ascii=False, indent=2))
        conn.close()
        raise SystemExit(1)

    cur.execute("UPDATE raw_material SET used=1 WHERE id=?", (picked["id"],))
    conn.commit()

    picked_dict = dict(picked)

    # Ready-made carousel specs store their content in source_file with
    # empty wrong/correct fields -- surface the actual file content instead.
    if not picked_dict.get("example_wrong") and picked_dict.get("source_file"):
        src_path = Path(picked_dict["source_file"])
        if not src_path.is_absolute():
            src_path = Path("/home/mike/compass-system") / src_path
        if src_path.is_file():
            picked_dict["ready_made_content"] = src_path.read_text(encoding="utf-8")
            picked_dict["ready_made_path"] = str(src_path)

    result = {
        "status": "ok",
        "picked": picked_dict,
        "total_rows": total,
        "rows_remaining_unused": unused_total - 1,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    conn.close()


if __name__ == "__main__":
    main()
