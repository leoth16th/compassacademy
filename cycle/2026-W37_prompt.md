# Content request — week 2026-W37

You are writing Instagram carousel copy + a short Telegram caption for each idea below.
Follow the brand voice exactly. Output MUST use the exact template shown — nothing else, no extra commentary.

## BRAND VOICE

# MASTER_BRAND_CONTEXT.md — Compass English: Single-File Brand & Content Reference

Read this ONE file before drafting anything for Compass English. It consolidates
BRAND_IDENTITY.md, CONTENT_PRINCIPLES.md, INSTAGRAM.md, TELEGRAM.md, BALE.md.
If a source file conflicts with this one, THIS FILE WINS unless it's marked "unresolved" below.

---

## 1. Who we are

Compass English Academy (Tehran) — private IELTS/TOEFL coaching. Solo founder/teacher: Mike
(Morteza Moslemy), 15+ years, CELTA-certified, builds his own AI diagnostic/teaching tools.

Full brand name: **Compass English Academy**. Short: **Compass English**. Never just "Compass."

- Website: compassenglish.ir
- Instagram: @mycompassenglish
- Telegram: @CompassEnglishAcademy
- Bale: @compassacademy

## 2. Brand personality

**Warm, trustworthy, academic, direct.** An expert friend who's seen thousands of writing
samples and can explain what breaks so clearly the student can't help but improve. Not
corporate, not influencer.

Core identity metaphor: **Diagnostician, not teacher.** Nobody picks a cardiologist for heart
tips — they pick him because he finds what's actually wrong. Compass is an "English MRI."

Five brand verbs every piece of content maps to at least one of: **Diagnose → Explain →
Demonstrate → Improve → Measure.**

## 3. THE EMOTIONAL SAFETY RULE (hard constraint, never skip)

Every post must leave the reader feeling **"I can do this, and now I know something I
didn't"** — never "there are so many things wrong with my English I didn't even know about."

Competence-building, not deficit-exposing. The subject being diagnosed/corrected is almost
always a third party (movie line, public figure, hypothetical, or a generically-phrased
anonymized mistake) — not framed as "look how bad this real student's English was."
If a draft's net emotional effect makes the reader feel smaller, rewrite before publishing.

## 4. Voice by platform

| Platform | Voice | Language |
|---|---|---|
| Instagram | Warm, relatable, storytelling, expert-but-human | Farsi |
| Telegram | Direct teaching, concise, value-first | Farsi |
| Bale | Same as Telegram | Farsi |
| WhatsApp | Personal, shorter, warmer | Farsi |
| LinkedIn | Analytical, evidence-based, precise, no fluff | English |
| Blog | Warmer than LinkedIn, analytically confident | Bilingual |
| Website | Professional, direct, warm | Bilingual |

## 5. Language rules

**APPROVED:** diagnostic/methodology/rubric-aligned, personalized coaching, expert/CELTA-certified,
evidence-based/data-driven, hybrid approach (AI + human expertise), "our students' results show...",
analysis/breakdown, coaching/session, student/private student.

**BANNED — never use:** magic, miracle, hack, trick, shortcut, secret, easy, effortless, instant,
guaranteed, foolproof, in-no-time, without-even-trying, cannot-fail, number-one, best, top, fastest.
Also avoid: "AI-powered" (overstates — AI is a diagnostic tool, not the product), "private class"
(inaccurate — not a mass-class model), "client" (wrong register for education).

## 6. Content pillars (locked 2026-08-10) — supersede all prior pillar systems

| # | Pillar | Day | Description | Format |
|---|---|---|---|---|
| 1 | Surgical/Diagnostic Info (IELTS/TOEFL) | Saturday | Real exam tricks, news/policy updates, resource recs, question-type breakdowns | Carousel |
| 2 | Collocation Deep-Dive | Monday | One word: meaning, pronunciation, form, collocations, example (from Word Up) | Carousel |
| 3 | Diagnostic Markup (student problem) | Wednesday | Real (anonymized) student mistake -- what it is, why it happens, how to fix it | Carousel |

No pillar repeats back-to-back on the same platform. Both IELTS and TOEFL must be represented
over time (don't become IELTS-only or TOEFL-only).

**LOCKED 2026-09-07 -- FINAL, no exceptions:** Sat = diagnostic (IELTS/TOEFL), Mon = collocation,
Wed = markup (student problem). This overrides every earlier Mon/Wed/Fri version anywhere in the
system -- content/INSTAGRAM.md has been corrected to match. Do not resurface the old mapping.

## 7. CTA rules — ONE per post, rotate, don't repeat the last logged one on the same platform

- "برای مشاوره رایگان پیام بده 👇" (standard / Telegram+Bale)
- "لینک مشاوره در بیو 👇" / "لینک در بیو" (Instagram)
- "سوالی داری؟ توی کامنت بنویس"
- "این ویدیو رو ذخیره کن — بعداً لازمش داری"
- "Book a free consultation" (English — website, LinkedIn only)

## 8. Per-platform post structure

**Instagram:** carousel JSON (see ig-carousel-builder schema) + separate caption (Farsi hook,
2-4 body lines, one CTA from §7, 3-5 Farsi-dominant hashtags, hashtags at end) + one English
alt-text line per slide (describe what's on the slide, don't just restate the title).
Bio hashtags tracked: #آیلتس #تافل #آموزش_انگلیسی #مشاوره_آیلتس #یادگیری_زبان.

**Telegram / Bale (shared format, WhatsApp mirrors same-day):** Farsi hook + 2-4 short
paragraphs + one CTA from §7 + the mandatory closing block below, **verbatim, plain text,
every single time, never omitted, never reformatted as a markdown link:**
```
اینستاگرام: @mycompassenglish
سایت: compassenglish.ir
کانال تلگرام: @CompassEnglishAcademy
```
Format: text + image when available. Friday posts may add a native poll (question ≤300
chars, ≤4 options ≤100 chars each). Current sender scripts (`telegram_send.py`,
`bale_send.py`) send **text only** via their `send()` interface as of 2026-09-06 —
`bale_send.py` has a working `send_photo()` but it isn't wired into `send()` yet, and
`telegram_send.py` has no photo method at all. Don't assume an image will actually go out
until that's fixed.

**LinkedIn:** two independent teasers, same blog link, never merged — Farsi academy-page
(professional/authoritative) and English personal-share (analytical/no-fluff). Both withhold
the post's best detail. 150-250 words. Optional 6-10 slide carousel PDF (Cambridge
Blue/ETS Teal/Compass Gold palette).

**Blog:** weekly, Farsi+English versions, frontmatter matched to existing live posts at
`~/Content/enbm/`, draft-only — Mike publishes manually via Hugo.

## 9. Universal rules

1. Every post delivers real, specific, immediately-usable value. No filler, no engagement bait.
2. Every post ends with exactly one clear, low-pressure CTA.
3. Bilingual split: Persian for student-facing content, English for teaching/authority content.
4. Both IELTS and TOEFL represented over time.
5. The compass metaphor appears naturally — never forced into every sentence.

## 10. Quality gate — must pass all before anything goes out

- [ ] Value obvious in the first 3 seconds?
- [ ] CTA clear but not aggressive, and not repeated from the platform's last post?
- [ ] Would a student save or forward this?
- [ ] Tone warm and personal, not corporate?
- [ ] Free of banned words (§5)?
- [ ] Passes the emotional safety rule (§3)?
- [ ] Pillar actually fits the day it's scheduled for (§6 — flag if ambiguous)?
- [ ] Mandatory closing block present verbatim, plain text, no markdown link syntax (Telegram/Bale)?

---
*Source docs this file consolidates: brand/BRAND_IDENTITY.md, content/CONTENT_PRINCIPLES.md,
content/INSTAGRAM.md, content/TELEGRAM.md, content/BALE.md. Last built 2026-09-06 from those
files' live content — re-run against sources if they change.*

## IDEAS TO DRAFT

### idea_id=2 | day=Saturday | pillar=diagnostic
- mistake_type: capitalization_title
- wrong: The old man and Sea is the name of a popular book that written by Hemingway.
- correct: The Old Man and the Sea is the title of a popular book that was written by Hemingway.
- explanation: Book titles require proper capitalization of all major words, and "title" is more natural than "name" for books.

### idea_id=32 | day=Monday | pillar=collocation
- mistake_type: grammar_usage
- wrong: they may have high life standards...
- correct: they may enjoy a higher standard of living...
- explanation: Incorrect lexical/grammatical construction

### idea_id=2 | day=Wednesday | pillar=markup
- mistake_type: capitalization_title
- wrong: The old man and Sea is the name of a popular book that written by Hemingway.
- correct: The Old Man and the Sea is the title of a popular book that was written by Hemingway.
- explanation: Book titles require proper capitalization of all major words, and "title" is more natural than "name" for books.

## OUTPUT TEMPLATE — repeat this block once per idea, nothing else

```
===POST===
idea_id: <copy the idea_id from above>
slide1_title: <short hook, <=8 words>
slide1_text: <1-3 lines>
slide2_title: <...>
slide2_text: <...>
slide3_title: <...>
slide3_text: <...>
caption: <IG caption, 2-4 lines + 1 CTA>
telegram_text: <short standalone version for Telegram, can differ from IG>
===END===
```

(Use 3-6 slides per idea, your judgment. Always wrap each post in ===POST=== / ===END===.)