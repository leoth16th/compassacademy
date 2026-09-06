# CAPABILITIES.md
Read this FIRST in any new session, before PROJECT_STATE.md.
This file changes rarely. If a tool/app exists, it's listed here — full stop.

## Content generation
- **Carousel builder** — Node app, `~/compass-system/ig-carousel-builder/`, serves http://localhost:4000
  - `GET /api/health` → contentDir + file count
  - `GET /api/content` → list files
  - `GET /api/render/:filename` → parsed slide JSON
  - Browser: `http://localhost:4000/?load=<filename>.txt`
  - INPUT FORMAT (real, confirmed via server.js): `handle:` / `bgColor:` / `textColor:` / `Slide N:` / `Badge:` / `Title:` / `Content:` / `Highlight:` fields. Human-readable draft style (`## SLIDE N`) is NOT builder input — it's a separate pre-draft format in `carousel-content/`.
  - Real input files live at `~/compass-system/ig-carousel-builder/carousel-inputs/`
- **claude-writer** — Goose recipe at `~/.config/goose/recipes/claude-writer.yaml`. Summons a fresh, memory-less Claude subagent via OmniRoute (localhost:20128). Text-only in/out. Every call needs full context restated — nothing persists.
- **Blog** — Hugo, `C:\Site\hugo-site-2-main` → compassenglish.ir
- **Image gen** — Seedream

## Posting channels
- Telegram — 2 bots, working
- Bale — bot, working
- WhatsApp Business — connected
- Instagram — carousel built locally, posted MANUALLY (no API path)
- LinkedIn — FULLY MANUAL. Iran-based LinkedIn Developer API access is blocked even through VPN. Do not attempt automation here.

## Infra
- OmniRoute — local model router, 127.0.0.1:20128, 121 models incl. auto/* free fallback
- control.db — SQLite, single source of truth for pipeline state (`~/compass-system/compassacademy/`)
- GitHub Actions — `github.com/leoth16th/compassacademy`, cron dispatches scheduled posts even if Mike's machine is off
- Notion — connected, only live productivity integration
- Gmail/Calendar — NOT connected

## Hard rules
- GOOSE_RULES.md: every success claim needs pasted real command output as proof. No proof → say "UNVERIFIED." Never fabricate tool output.
- CONTENT_CALENDAR.md is auto-generated FROM control.db. Never hand-edit it.
