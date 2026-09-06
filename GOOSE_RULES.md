# Core Rule — No Claims Without Proof

- Never claim a fix is done, a test passed, or a file changed without pasted terminal output or direct tool output confirming it.
- If a test is unclear, loop until it is clear (run it again with different parameters) rather than guessing.
- When something does not work, check boring explanations first (e.g., timezone, file path, environment variables) before assuming a deeper bug.

# GOOSE Rules — Enforcement Patterns for Compass System

**Last Updated:** 2026-08-29  
**Purpose:** Structural rules that prevent recurring failure modes. These are NOT guidelines — violations block automation.

---

## RULE 1: Never Print "Sent" Without Real Proof

**Statement:**  
Every sender function and dispatch script must print success only AFTER verifying the real API response. "Sent," "posted," "done," or any success claim must be backed by documented proof — either:
- Actual HTTP response code 200-299 from the platform API
- Database query result showing sent_log row actually exists
- Exception raised if send fails (no silent failures)

**Violation Examples (FORBIDDEN):**
```python
# ❌ WRONG: prints success before checking response
print("OK - sent to Telegram")
result = api_call(token, "sendMessage", payload)  # After print!

# ❌ WRONG: prints success unconditionally
try:
    response = requests.post(url, data)
finally:
    print("posted")  # Even if exception occurred
```

**Correct Examples (REQUIRED):**
```python
# ✓ RIGHT: checks response before printing
result = api_call(token, "sendMessage", payload)
if not result.get("ok"):
    raise RuntimeError(f"Telegram send failed: {result}")
print(f"✓ sent to Telegram (response_id={result['result']['message_id']})")

# ✓ RIGHT: verifies DB state
sender(content, idempotency_key)
if not already_sent(db, idempotency_key):
    raise RuntimeError("Send function returned but DB shows not sent")
print(f"✓ posted {id} (verified in sent_log)")
```

**Enforcement:**
- Code review: every print statement with success/sent/posted/done must trace back to real response check
- Logs: success must include proof reference (API response code, DB row ID, etc.)
- Tests: deliberately fail sender mock, verify error is raised (not silent "sent" print)

---

## RULE 2: Every Script Must Self-Load Its Environment

**Statement:**  
Scripts that read environment variables must call `load_dotenv()` at module import time. No script should silently depend on interactive shell having sourced `.env` beforehand. This applies to all Python files in `senders/`, `scripts/`, and root-level dispatch scripts.

**Required Pattern:**
```python
from pathlib import Path
from dotenv import load_dotenv

# Load .env from repo root
REPO_ROOT = Path(__file__).parent.parent  # or appropriate relative path
load_dotenv(str(REPO_ROOT / ".env"))

# Now read env vars safely
API_TOKEN = os.environ.get("MY_TOKEN")
```

**Violation Check:**
```bash
grep -l "os.environ.get" senders/*.py scripts/*.py | while read f; do
  if ! grep -q "load_dotenv" "$f"; then
    echo "VIOLATION: $f reads env vars but doesn't load .env"
  fi
done
```

---

## RULE 3: Carousel Input Must Validate Before Builder

**Statement:**  
Every carousel input file must pass `validate_carousel_format.py` BEFORE being passed to the carousel builder (`ig-carousel-builder/export-carousels.js`). Format mismatches must fail loudly, not silently produce empty slides or malformed images.

**Required Workflow:**
```bash
# 1. Draft carousel (claude-writer or manual)
goose load(source: "content-draft.yaml", parameters: {...})

# 2. Save to carousel-content/w{week}_{topic}_{lang}.txt
cp draft.txt carousel-content/w36_topic_en.txt

# 3. VALIDATE — must exit 0
python3 scripts/validate_carousel_format.py carousel-content/w36_topic_en.txt
if [ $? -ne 0 ]; then
  echo "ABORT: carousel format invalid, fix before building"
  exit 1
fi

# 4. Export images
node ig-carousel-builder/export-carousels.js carousel-content/w36_topic_en.txt
```

**Violation Examples (FORBIDDEN):**
```bash
# ❌ WRONG: skip validator, builder silently produces wrong images
node ig-carousel-builder/export-carousels.js malformed.txt  # 0 slides output, no error

# ❌ WRONG: assume format is correct
# Later: "Why are carousels blank?" → formatter skipped, format was wrong
```

---

## RULE 4: Canonical Formats Must Have Single Source of Truth

**Statement:**  
If a format or invocation pattern appears in multiple places (docs, examples, code comments), there must be ONE canonical file that all other references point to. Scatter defeats amnesia-prevention.

**Current Canonical Files:**
- `ig-carousel-builder/CAROUSEL_FORMAT.md` — carousel input spec
- `AGENTS.md` — agent/recipe invocation guide
- `GOOSE_RULES.md` — this file, enforcement patterns

**Violation Check:**
```bash
# Every reference to carousel format should point to CAROUSEL_FORMAT.md
grep -r "Slide 1:" docs/ notes/ README.md 2>/dev/null | grep -v CAROUSEL_FORMAT.md
# If output is non-empty, you have duplicated format definition
```

---

## RULE 5: Test Mode for All Sends (Never Live During Development)

**Statement:**  
During development, testing, or integration work, all sender calls must use test chat IDs / channels, never production channels. No real sends to @CompassEnglishAcademy, @compassacademy, or Mike's personal chat unless explicitly agreed.

**Test Channel Setup:**
```bash
# .env.test (for local testing)
TELEGRAM_BOT_TOKEN_1=<test_bot_token>
TELEGRAM_CHAT_ID=<your_test_chat_id>
BALE_BOT_TOKEN=<test_bot_token>
BALE_CHAT_ID=<test_channel>
```

**Activation:**
```python
# Load test env if testing
if os.environ.get("GOOSE_TEST_MODE"):
    load_dotenv(".env.test")
```

---

## Enforcement Chain

1. **Code Review:** Every PR must pass these rule checks
2. **Pre-commit Hook:** Validate carousel format + env-loading on commit (optional, but recommended)
3. **Integration Tests:** Test suite deliberately triggers errors, verifies correct exception handling
4. **Documentation:** New sessions inherit these rules via this file + AGENTS.md + CAROUSEL_FORMAT.md

---

## See Also

- `AGENTS.md` — Agent invocation rules
- `CAROUSEL_FORMAT.md` — Carousel input format specification
- `senders/telegram_send.py` — Example of correct send with response verification
