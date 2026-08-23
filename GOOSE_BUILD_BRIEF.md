# Compass content cycle — build brief for Goose

Run this with `goose run -i GOOSE_BUILD_BRIEF.md -s` from the repo root
(create the repo first with `git init` if it doesn't exist yet).

## Non-negotiable rule

Goose is labor, not a writer. Every recipe in this system takes
already-finished content (captions, copy, asset paths) supplied in a
manifest file and moves it through a state machine, git, and scheduled
sending. No recipe here may draft, rewrite, or suggest content — that
happens in a separate Claude conversation, and the result lands in
`cycle/<week_id>/manifest.yaml` before Goose ever touches it. If a recipe
run is ever asked to "write a caption" or "come up with a post," refuse
and tell Mike to take it to Claude first.

## What to build, in order

1. Directory layout (repo root):
```
control.db
schema.sql
cycle/                 (working folder, one subfolder per open week)
senders/
  dispatch_due.py
  telegram_send.py     (Mike ports his existing script here)
  bale_send.py         (Mike ports his existing script here)
recipes/
  cycle-status.yaml
  cycle-intake.yaml
  cycle-close.yaml
  cycle-archive.yaml
.github/workflows/
  publish-cycle.yml
archive/                (add to .gitignore — never pushed)
```

2. `sqlite3 control.db < schema.sql` — creates `cycles` and
   `content_items`. Confirm with `.tables` and `.schema content_items`.

3. Drop in the four provided recipe files exactly as given — don't add
   instructions beyond what's written in them. Run `goose recipe validate`
   on each before relying on it.

4. `senders/dispatch_due.py` is a skeleton. Wire Mike's existing
   Telegram/Bale Python (he already has working senders, currently
   hardcoded-token scripts) into `telegram_send.py` / `bale_send.py`. Keep
   the idempotency check in `dispatch_due.py` — it's what stops
   double-posting, never remove it.

5. Move real tokens out of any script and into GitHub Actions secrets:
   `TELEGRAM_BOT_TOKEN_1`, `TELEGRAM_BOT_TOKEN_2`, `BALE_BOT_TOKEN`, plus
   anything else the ported senders need. Confirm the exact secret names
   with Mike before touching real credentials.

6. Add `archive/` (and any other local-only paths) to `.gitignore`.

7. Verify GitHub Actions actually runs on Mike's account/repo — schedule
   trigger fires, secrets resolve — before relying on it. Confirm, don't
   assume: Iran-based accounts have run into GitHub service restrictions
   before. If Actions doesn't work reliably, tell Mike and fall back to
   any always-on host you can reach (a VPS, or a free cron-webhook
   service) running `dispatch_due.py` on the same schedule — the script
   doesn't care where it runs, only that the machine isn't Mike's laptop.

## The weekly cycle, step by step

1. Mike gives Claude the week's raw material (as already happens
   Thursdays). Claude drafts everything and writes
   `cycle/<week_id>/manifest.yaml` — format below. This step never
   touches Goose.
2. Mike runs the `cycle-intake` recipe with that manifest. Goose loads it,
   walks Mike through explicit per-item approval, writes to `control.db`.
3. Mike can run `cycle-status` any time to see where the week stands.
4. Once everything is approved, Mike runs `cycle-close`. Goose splits
   manual vs automated, stages automated items under `cycle/<week_id>/`,
   writes `schedule.json`, commits and pushes, and tells Mike exactly
   which platforms need him to post by hand this week.
5. Mike does the manual posts. The GitHub Actions workflow polls every
   15 minutes and fires the automated ones at their scheduled time — this
   is what keeps working even if Mike's machine is off.
6. Once everything shows `posted`, Mike runs `cycle-archive`. Goose copies
   `cycle/<week_id>/` to a local, non-git archive folder, removes it from
   the repo, and commits the removal — repo stays slim, history survives
   on disk.

## Manifest format Claude will hand Goose (example)

```yaml
week_id: "2026-W35"
items:
  - platform: telegram
    pillar: collocation
    post_date: "2026-08-25"
    post_time: "09:00"
    mode: automated
    content_path: cycle/2026-W35/telegram/mon-collocation.md
  - platform: linkedin
    pillar: diagnostic
    post_date: "2026-08-22"
    post_time: null
    mode: manual
    content_path: cycle/2026-W35/linkedin/sat-diagnostic.md
```

## Open questions — bring these back from Goose, or verify yourself

- Confirm GitHub Actions scheduled workflows actually run reliably on
  Mike's account (see step 7 above — this needs a real test).
- Decide whether `control.db` itself should be git-tracked (simple, but
  SQLite binary diffs are noisy in `git log`) or whether Goose should
  export a plain-text `state.json` dump alongside it for cleaner review.
- Locate exactly where the existing Telegram/Bale Python senders live
  today, so their real logic — not the skeleton — gets ported into
  `senders/`.
