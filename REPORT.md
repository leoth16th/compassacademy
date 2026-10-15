# Compass English Academy - Report (2026-10-15)

Single status file. Replaces CHANGELOG, MUST_READ_AFTER_OCT3 and the two AUDIT reports.

## Goal
Students share posts with their own followers, which puts the academy in front of their circles.
Not virality: no budget for high-production video. Clean, professional, high-quality content.

## Pillars (changed 2026-10-15)
| Day | Pillar (DB name) | Source |
|---|---|---|
| Saturday | `entertainment` - songs / news / entertainment | no DB rows; Mike brings the topic. Urgent exam/policy news still qualifies. Never reproduce song lyrics |
| Monday | `collocation` | raw_material.db |
| Wednesday | `student_mistake` | raw_material.db - favor specific, embarrassing errors ("4 hidden errors in one sentence") |

Old `test_info` (14 ready-made exam carousels, 11 unused) stays in the bank. Use it only by typing `test_info`.
Pillar is defined in: `scripts/pick_idea.py`, `scripts/stage_interactive.py`, `scripts/calendar_watcher.py`,
and `~/compass-system/MASTER_BRAND_CONTEXT.md` section 6 (what the web AI reads). Backup: `MASTER_BRAND_CONTEXT.md.bak-2026-10-15`.

## How to post
Desktop icon "Compass Daily" -> `scripts/daily.sh` -> `stage_interactive.py`. Pillar prompt accepts saturday / monday / wednesday.
Stages Telegram + Bale, pushes to GitHub, Actions sends at 08:00 Tehran.
LinkedIn and IG are manual. LinkedIn: post from BOTH the Academy page and the personal profile, mention both at the end. The Academy page should grow its own followers.

## Automation status
- Working since 2026-09-14. Fixed: missing python-dotenv in requirements, control.db was gitignored, absolute paths in DB (dispatch_due.py now re-anchors to repo root).
- Workflow runs 3x daily (04:30, 05:00, 05:30 UTC) because GitHub cron silently skipped a day on 09-19. Re-runs are safe: only `state=staged` rows are sent, plus a `sent_log` dedup.
- If a day is missed: `gh workflow run publish-cycle.yml` from `compassacademy/`.
- Parspack cPanel host has no SSH and no Python. Only possible helper is a PHP cron that pings the GitHub API. Not set up.

## Performance findings (2026-08-29 to 2026-10-04)
Instagram (73 followers on 10-13):
- Reach 34-123 per post, above follower count, so posts do travel. Shares mostly 4-10 since mid-September; peaks 21-22.
- Best shares: 09-16 "4 hidden errors" (student_mistake, 22) and 08-29 exam-access news (21).
- Weakest: single-word vocabulary/collocation posts. Late posts drifted into generic exam tips and shares fell.
- Posting paused 10-04 to 10-13; daily reach fell from ~55-85 to 1-11.
LinkedIn (21 posts, 3,274 impressions, 0 follows):
- Daily Persian posts got 15-57 impressions each. Almost nobody sees them.
- Outliers: 08-05 video "memorized templates cap you at Band 4" (2,112) and 08-29 English exam-access news (520).
- Reposts (constant 1) and CTR columns look unreliable.
- Company-page post then reshare to personal profile gets almost no reach. Post natively from both.
Lesson: what gets forwarded is urgent or surprising and specific. Evergreen tips do not.

## Next steps
1. Resume posting with the new pillars.
2. Review in about 3 weeks: IG shares and follower count vs the numbers above; LinkedIn from both accounts.
3. Weekly: look for real exam/policy news affecting Iranian candidates (Perplexity is fine for this).
4. Competitor research (small individual IELTS/TOEFL teachers) is run through Hermes. Prompt: `/home/mike/hermes-ig-analysis-prompt.txt`.

## Dead or stale - do not use
`scripts/build_week_prompt.py`, `import_week.py`, `fetch_telegram_inbox.py`, `cycle/`, `agents/` (old Mon/Wed/Fri days).
Goose and recipes are retired. Reference docs not touched and possibly stale: CAPABILITIES.md, GOOSE_RULES.md, HOW_TO_USE_CLAUDE_WRITER.md, README.md, START-HERE.md.
