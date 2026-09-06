# How to Use Claude-Writer (Tested, Working)

**Last Updated:** 2026-08-30 05:30 UTC  
**Status:** ✓ Verified working (tested 2026-08-30)

---

## Quick Start

Claude-writer is a **chat-only content creation subagent** (Farsi language). It does NOT have tool access.

**Correct invocation (TESTED):**

```
delegate(
  source: "claude-writer",
  extensions: [],
  instructions: "Your task here in plain language"
)
```

**Critical constraints:**
- `extensions: []` — empty array, NO tools allowed
- Chat-only route (route 6 / high-copy)
- NO tool-calling in instructions
- Output language: **Farsi (Persian)**

---

## What It Does

Claude-writer is configured to:
- Write content in **Farsi** (Persian language)
- Follow Compass Academy branding (diagnostic positioning, not generic IELTS)
- Draft for: Instagram, LinkedIn, Telegram, Bale/WhatsApp
- NO web search, NO tool calling, NO external APIs

---

## How to Invoke (Step by Step)

### Step 1: Use `delegate()` function

```python
delegate(
  source: "claude-writer",
  extensions: [],  # CRITICAL: empty array, no tools
  instructions: "Write a 3-sentence intro to test anxiety for Instagram"
)
```

### Step 2: Wait for response

Claude-writer will:
1. Process your instruction
2. Generate content in Farsi
3. Return it (no external calls, no tools needed)

### Step 3: Check output

Response will be in **Farsi**. Example:

```
من دستیار محتوا و استراتژی کراسپلتفرم آکادمی Compass English هستم...
```

---

## Real Working Example (Tested 2026-08-30)

**Invocation:**
```
delegate(
  source: "claude-writer",
  extensions: [],
  instructions: "Who are you? What is your job in the Compass system? Answer in 2-3 sentences."
)
```

**Response (in Farsi):**
```
من دستیار محتوا و استراتژی کراسپلتفرم آکادمی Compass English هستم — طبق چارچوبی که برام تعریف شده، محتوا رو برای اینستاگرام، لینکدین، تلگرام و واتساپ/بله طراحی، برنامهریزی و بریف میکنم، با محوریت پوزیشنینگ «دیاگنوستیک» آکادمی (نه یک صفحهی معمولی آموزش آیلتس).

مهم است بدانید: من یک زبان مدل هوش مصنوعی (Claude، ساختهی Anthropic) هستم که در قالب یک سابایجنت در فریمورک goose اجرا شدهام — نه یک عضو واقعی تیم یا سیستم اختصاصی به نام «Compass». دستورالعملهای بالا صرفاً یک پرامپت/برندبوک هستند که به من داده شده تا محتوا مطابق آنها تولید کنم.
```

**Translation (for reference):**
> I am a cross-platform content and strategy assistant for Compass English Academy — according to the framework defined for me, I design, plan, and brief content for Instagram, LinkedIn, Telegram, and Bale/WhatsApp, with focus on the Academy's diagnostic positioning (not a generic IELTS teaching page).
>
> Important to know: I am an AI language model (Claude, made by Anthropic) running as a subagent in the goose framework — not a real team member or specialized system called "Compass." The above instructions are merely a prompt/brand book given to me to generate content according to them.

---

## What NOT to Do

### ❌ WRONG: Passing tool-requiring instructions

```python
# WILL FAIL with "Bad request (400): No target in combo high-copy supports tool calling"
delegate(
  source: "claude-writer",
  extensions: [],
  instructions: "Search the web for IELTS test dates and write about them"
)
```

**Why:** Web search is a tool. Chat-only route doesn't support tools.

### ❌ WRONG: Using old `content-draft.yaml` recipe directly

```python
# OUTDATED - don't use this
load(source: "content-draft.yaml", parameters: {...})
```

**Why:** This may have different configuration. Use `delegate(source: "claude-writer", ...)` instead.

### ❌ WRONG: Including tools in extensions

```python
# WILL FAIL
delegate(
  source: "claude-writer",
  extensions: ["web_search", "file_read"],  # NO tools allowed
  instructions: "..."
)
```

---

## Workflow: Draft → Review → Post

1. **Draft** (use claude-writer)
   ```
   delegate(
     source: "claude-writer",
     extensions: [],
     instructions: "Draft a Telegram post about IELTS Writing band descriptors in Farsi"
   )
   ```

2. **Review** (human approval via PROJECT_STATE.md workflow)
   - Read the Farsi output
   - Verify tone, accuracy, brand alignment
   - Do NOT auto-post

3. **Post** (manual or via dispatch_due.py)
   - Copy approved content to carousel-content/ or posting/
   - Run carousel builder if needed
   - Dispatch via telegram_send.py or bale_send.py

---

## Output Language: Farsi

Claude-writer is configured to output **only in Farsi (Persian)**. 

If you need English:
- Draft in claude-writer (gets Farsi)
- Translate via separate translation step (not part of claude-writer)
- Or use different agent with English configuration

---

## Timeout & Limits

- Max turns: ~25 per subagent session (inherited from recipe config)
- Timeout: Use default (typically 60-120 seconds)
- No streaming output (synchronous call)

---

## Troubleshooting

### Error: "Bad request (400): No target in combo high-copy supports tool calling"

**Fix:** Remove any tool-requiring instructions. Ensure `extensions: []` is set.

```python
# WRONG (will trigger error)
delegate(
  source: "claude-writer",
  instructions: "Search for IELTS dates and write about them"
)

# RIGHT (will work)
delegate(
  source: "claude-writer",
  extensions: [],
  instructions: "Write about IELTS Writing band descriptors based on your knowledge"
)
```

### Error: Response is in English instead of Farsi

**Fix:** Check if you're using the correct route. Verify recipe config is set to Farsi output.

### Response is generic/not brand-aligned

**Fix:** Include specific brand guidance in instructions:

```python
delegate(
  source: "claude-writer",
  extensions: [],
  instructions: """
  Write a Telegram post about IELTS Writing Task 1 (letter writing).
  
  Brand constraints:
  - Diagnostic positioning (focus on exam mechanics/scoring, not generic tips)
  - 2-3 short paragraphs
  - Actionable insight specific to band advancement
  - Tone: direct, not marketing-y
  """
)
```

---

## See Also

- `PROJECT_STATE.md` — Current system status + canonical docs list
- `GOOSE_RULES.md` — Structural rules (env-loading, no false "sent" claims)
- `CAROUSEL_FORMAT.md` — Carousel input format (if building Instagram carousels)

---

## Historical Note (Session 7 Correction)

**Previous claim (WRONG):** "AGENTS.md documents claude-writer invocation"

**Reality (2026-08-30):** AGENTS.md was outdated. This file (HOW_TO_USE_CLAUDE_WRITER.md) is the **current tested invocation**, verified working with real subagent execution on 2026-08-30 05:30 UTC.

Do not trust old session logs. Trust only this file + the test proof at the top.
