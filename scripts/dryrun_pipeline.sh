#!/usr/bin/env bash
# dryrun_pipeline.sh — end-to-end mechanics test of the content pipeline
# using ONLY fake data. Never touches real control.db, real cycle folders,
# or real Telegram/Bale (network layer is stubbed).
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"   # canonical repo root
W="/tmp/dryrun_pipeline"
rm -rf "$W"; mkdir -p "$W/cycle/1999-W01/telegram" "$W/cycle/1999-W01/bale" "$W/cycle/1999-W01/linkedin" "$W/senders"

FAIL=0
check() { # check <desc> <cmd>
  if eval "$2" >/dev/null 2>&1; then echo "  ✅ $1"; else echo "  ❌ $1"; FAIL=1; fi
}

echo "== 1. Build isolated fake world =="
sqlite3 "$W/control.db" < "$ROOT/schema.sql"
sqlite3 "$W/control.db" "
INSERT INTO cycles VALUES ('1999-W01','open',datetime('now'),NULL,NULL);
INSERT INTO content_items (id,week_id,platform,pillar,post_date,post_time,mode,content_path,idempotency_key,state)
VALUES
 ('1999-W01-telegram-collocation','1999-W01','telegram','collocation','1999-01-04','09:00','automated','cycle/1999-W01/telegram/mon.md','1999-W01:telegram:1999-01-04','intake'),
 ('1999-W01-bale-diagnostic','1999-W01','bale','diagnostic','1999-01-05','10:30','automated','cycle/1999-W01/bale/sat.md','1999-W01:bale:1999-01-05','intake'),
 ('1999-W01-linkedin-diagnostic','1999-W01','linkedin','diagnostic','1999-01-02',NULL,'manual','cycle/1999-W01/linkedin/sat-li.md','1999-W01:linkedin:1999-01-02','intake');"
echo "fake draft content" > "$W/cycle/1999-W01/telegram/mon.md"
echo "fake draft content" > "$W/cycle/1999-W01/bale/sat.md"
echo "fake draft content" > "$W/cycle/1999-W01/linkedin/sat-li.md"

echo "== 2. Simulate intake approval (as cycle-intake does per item) =="
sqlite3 "$W/control.db" "UPDATE content_items SET state='approved', approved_by='DRYRUN', approved_at=datetime('now') WHERE week_id='1999-W01';"
check "all 3 approved" "[ \$(sqlite3 $W/control.db \"SELECT COUNT(*) FROM content_items WHERE state='approved'\") = 3 ]"

echo "== 3. Simulate cycle-close split (automated->staged, manual->manual_pending) =="
sqlite3 "$W/control.db" "UPDATE content_items SET state=CASE WHEN mode='automated' THEN 'staged' ELSE 'manual_pending' END WHERE week_id='1999-W01';"
check "automated staged (=2)"   "[ \$(sqlite3 $W/control.db \"SELECT COUNT(*) FROM content_items WHERE state='staged'\") = 2 ]"
check "manual_pending (=1)"     "[ \$(sqlite3 $W/control.db \"SELECT COUNT(*) FROM content_items WHERE state='manual_pending'\") = 1 ]"

echo "== 4. Dispatch with STUB network (real dispatcher code, no real sends) =="
cp "$ROOT/senders/dispatch_due.py" "$W/senders/"
cat > "$W/senders/telegram_send.py" <<'EOF'
def send(content, idempotency_key): print(f"[STUB-TG] {idempotency_key} <- {content.strip()[:20]}")
EOF
cat > "$W/senders/bale_send.py" <<'EOF'
def send(content, idempotency_key): print(f"[STUB-BALE] {idempotency_key} <- {content.strip()[:20]}")
EOF
echo "-- dispatch run 1 (from fake repo root, as production does) --"
( cd "$W" && python3 senders/dispatch_due.py --db control.db )

echo "-- dispatch run 2 (idempotency proof) --"
( cd "$W" && python3 senders/dispatch_due.py --db control.db )

echo "== 5. Assertions =="
check "telegram item posted"     "[ \"\$(sqlite3 $W/control.db \"SELECT state FROM content_items WHERE id='1999-W01-telegram-collocation'\")\" = 'posted' ]"
check "bale item posted"         "[ \"\$(sqlite3 $W/control.db \"SELECT state FROM content_items WHERE id='1999-W01-bale-diagnostic'\")\" = 'posted' ]"
check "linkedin untouched (manual_pending)" "[ \"\$(sqlite3 $W/control.db \"SELECT state FROM content_items WHERE id='1999-W01-linkedin-diagnostic'\")\" = 'manual_pending' ]"
check "sent_log has exactly 2 rows" "[ \$(sqlite3 $W/control.db \"SELECT COUNT(*) FROM sent_log\") = 2 ]"
check "rerun added NO new sends (sent_log still 2 -> idempotent)" "[ \$(sqlite3 $W/control.db \"SELECT COUNT(*) FROM sent_log\") = 2 ]"
check "no failed states" "[ \$(sqlite3 $W/control.db \"SELECT COUNT(*) FROM content_items WHERE state='failed'\") = 0 ]"

echo ""
[ $FAIL -eq 0 ] && echo "RESULT: ✅ ALL CHECKS PASSED — pipeline mechanics verified end-to-end" || echo "RESULT: ❌ FAILURES ABOVE"
exit $FAIL
