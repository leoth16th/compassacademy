# PROJECT_STATE.md — Single Cold‑Start Entry Point

This file is the canonical source of truth for the compass‑system project. All claims below are backed by real execution output from the session dated 2026‑08‑30.

## Proven Facts (Verified by Real Tests)

- **Env‑loading fix**: `telegram_send.py`, `bale_send.py`, and `calendar_watcher.py` now call `load_dotenv()` at import. Tested with `env -i` — token loads correctly in a clean environment.  
  *Proof:* `env -i python3 -c "from senders.telegram_send import send; ..."` succeeded.

- **False‑sent prevention**: `dispatch_due.py` now wraps the sender call in `try/except`. If the sender raises an exception, the script exits with code 1 and does **not** mark the item as sent in the DB.  
  *Proof:* Tested with a broken token and a past post_date (`2020-01-01`); script exited 1 and DB remained unchanged.

- **Claude‑writer invocation**: Works correctly with `delegate(source: 'claude-writer', extensions: [], instructions: ...)`. The subagent runs in chat‑only mode (no tools) and outputs Farsi text as requested.  
  *Proof:* Actual invocation produced the expected Farsi reply. Canonical usage documented in `HOW_TO_USE_CLAUDE_WRITER.md`.

- **Carousel app real location**: The live app runs from `~/compass-system/ig-carousel-builder/` (PID 102886). Its `server.js` uses `CONTENT_DIR = join(__dirname, 'carousel-inputs')`.  
  *Endpoints:* `/api/health`, `/api/content`, `/api/render/:filename`.  
  *Proof:* Read `server.js` directly; confirmed with `curl` calls.

- **Carousel text formatting fix**: Default alignment changed from `'right'` to `'center'` and `contentBold` to `true` in `App.jsx`, `CarouselPreview.jsx`, and `ColorStyling.jsx`. CSS edits alone were insufficient because inline styles override them.  
  *Proof:* After applying the changes and rebuilding (`npm run build`), the carousel preview displays text centered and bold.

- **Canonical file locations**:
  - Carousel input files: `~/compass-system/ig-carousel-builder/carousel-inputs/` (contains 8 `.txt` files for Week 36).
  - Carousel app URL: `http://localhost:4000/?load=<filename>.txt`.

## Canonical Documentation Files

| File | Purpose |
|------|---------|
| `GOOSE_RULES.md` | Structural enforcement rules for all agents (now includes the Core Rule). |
| `PROJECT_STATE.md` | This file — the master entry point with proven facts and operational notes. |
| `HOW_TO_USE_CLAUDE_WRITER.md` | Step‑by‑step guide for invoking the Farsi‑writing subagent. |
| `CAROUSEL_FORMAT.md` | Spec for the input format used by the carousel builder. |

## Resolved Items

- ✅ Env‑loading amnesia (all scripts now self‑load `.env`).
- ✅ False‑sent reporting (exception handling added, DB updates only on success).
- ✅ Claude‑writer invocation (fixed by using `extensions: []` and proper instructions).
- ✅ Carousel builder format amnesia (real app location and endpoints identified).
- ✅ Carousel text formatting (hardcoded defaults changed to center + bold).

## Operational Tricks

- When testing `dispatch_due.py`, use `post_date='2020-01-01'` and `mode='automated'` to eliminate timezone ambiguity.
- Always rebuild the carousel app after changing source files: `cd ~/compass-system/ig-carousel-builder && npm run build`.
- The carousel validator should test against real files in `carousel-inputs/` using the `/api/render` endpoint, not synthetic files.
- To check carousel app health: `curl http://localhost:4000/api/health`.

## Stale / Archive Documents

The following documents have been moved to `ARCHIVE_DO_NOT_READ_STALE_DOCS/` because they are superseded or no longer accurate:
- `AGENTS.md` (superseded by `HOW_TO_USE_CLAUDE_WRITER.md`)
- `CAROUSEL_TEXT_FORMATTING_FIX.md` (fixed and deployed; see above)
