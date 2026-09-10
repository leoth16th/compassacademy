#!/usr/bin/env python3
"""
Pure logic idea-picker. No LLM. No agent. Extracted from recipes/pick-idea.yaml
so it runs standalone with zero Goose/agent overhead.

Usage:
  python3 pick_idea.py                  # any unused idea
  python3 pick_idea.py collocation      # unused idea for this pillar, fallback any
"""
import sqlite3
import json
import sys

DB = "/home/mike/compass-system/raw_material.db"


def main() -> None:
    pillar = sys.argv[1].strip() if len(sys.argv) > 1 else ""

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

    result = {
        "status": "ok",
        "picked": dict(picked),
        "total_rows": total,
        "rows_remaining_unused": unused_total - 1,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    conn.close()


if __name__ == "__main__":
    main()
