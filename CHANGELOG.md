# Compass System — Changelog

## Session 7 (2026-08-29 22:39 UTC) — OVERNIGHT DEEP FIX LOOP

### Structural Fixes (All Completed)

**FIXED: Environment-Loading Amnesia**
- Added `load_dotenv()` to all sender scripts
- Files: `senders/telegram_send.py`, `senders/bale_send.py`, `scripts/calendar_watcher.py`
- Evidence: All files now call `load_dotenv(str(REPO_ROOT / ".env"))` at import time
- Benefit: Scripts now work standalone; no longer depend on interactive shell sourcing .env

**FIXED: False "Sent" Reports**
- Wrapped sender call in dispatch_due.py with try/except
- Success message now printed ONLY after sender completes without exception
- Evidence: Lines 88-91 in senders/dispatch_due.py now check exception before printing "✓ posted"
- Benefit: Eliminates silent failures being reported as success

**FIXED: Claude-Writer Invocation Amnesia**
- Created `AGENTS.md` (191 lines) with canonical claude-writer recipe invocation
- Includes copy-pasteable example with real parameters
- Evidence: File exists with working example showing topic/platform/tone/context parameters
- Benefit: New sessions inherit single canonical reference, not scattered session logs

**FIXED: Carousel Format Amnesia**
- Created `ig-carousel-builder/CAROUSEL_FORMAT.md` (151 lines) with full spec
- Created `scripts/validate_carousel_format.py` (207 lines) validator
- Evidence: Both files created and tested; validator accepts old markdown + new header/slide formats
- Benefit: Format conflicts eliminated; validator prevents malformed slides before builder

### Documentation Created

- `GOOSE_RULES.md` (170 lines) — Structural enforcement rules for 4 critical patterns
- `AGENTS.md` (191 lines) — Single canonical agent invocation guide
- `ig-carousel-builder/CAROUSEL_FORMAT.md` (151 lines) — Carousel input format spec
- `scripts/validate_carousel_format.py` (207 lines) — Format validator (both formats)

### Documentation Consolidated

- `PROJECT_STATE.md` rewritten: 654 lines → 69 lines (current state only, linked to canonical docs)
- Created `CHANGELOG.md` (this file) to preserve dated history

### Code Changes

- `senders/telegram_send.py`: Added load_dotenv() + Path import
- `senders/bale_send.py`: Added load_dotenv() + Path import
- `scripts/calendar_watcher.py`: Replaced manual .env loader with load_dotenv()
- `senders/dispatch_due.py`: Wrapped sender call in try/except, conditional success print

---

## Session 6 (2026-08-26 afternoon) — CLAUDE DRAFTING PATH OPERATIONAL

### Status
- Claude-writer subagent tested and working (via content-draft.yaml recipe)
- Carousel builder verified working (images render, upload to posting/)
- w36 sanctions carousel created, drafted by claude-writer, built, posted to Telegram/Bale
- Scheduled content locked (w36 three-day manifest frozen in cycle/)

### Changes
- content-draft.yaml recipe created (custom_omnirouter_3, model=high, no tools)
- dispatch_due.py idempotency logic tested (marks sent_log, prevents re-sends)
- calendar_watcher.py running daily (monitors 3 pillar slots)

---

## Session 5 (2026-08-22) — INFRASTRUCTURE VERIFIED

### Status
- Telegram bot tokens working (TOKEN_1, TOKEN_2 failover tested)
- Bale API working (custom HTTP wrapper, no client library needed)
- Database schema verified (control.db, content_items + sent_log tables)
- Carousel builder (Node.js + Vite) running on localhost:5173

### Changes
- telegram_send.py idempotency implemented (message_id tracking)
- bale_send.py idempotency implemented (custom message ID tracking)
- dispatch_due.py workflow implemented (fetch due_items, send, mark_sent/posted)

---

## Earlier Sessions (W35)

- Initial carousel builder setup (ig-carousel-builder/)
- First content cycle (W35 diagnostic, collocation, markup)
- Telegram + Bale sender implementations (Python, no external deps for sends)
- control.db schema design (SQLite, idempotency via sent_log)
