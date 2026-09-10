#!/usr/bin/env bash
# Daily content helper. Carousel build, IG post, LinkedIn post, telegram pic
# creation stay manual. This script covers everything else.
#
# Usage:
#   ./daily.sh                            -> interactive: asks you everything, stages + pushes
#   ./daily.sh post                       -> same as above
#   ./daily.sh idea [pillar]              -> print an unused idea, mark it used
#   ./daily.sh stage --platform telegram --date YYYY-MM-DD --text-file f [--image f] [--pillar p]
#                                          -> queue a post (non-interactive)
#   ./daily.sh push                       -> commit + push control.db + posting/
#   ./daily.sh send-telegram <img> <text> -> send photo+caption to Telegram RIGHT NOW
#   ./daily.sh send-bale <text>           -> send text to Bale RIGHT NOW

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SENDERS_DIR="$(cd "$SCRIPT_DIR/../senders" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cmd="${1:-}"

case "$cmd" in
  ""|post)
    python3 "$SCRIPT_DIR/stage_interactive.py"
    echo ""
    python3 "$SCRIPT_DIR/blog_interactive.py"
    ;;

  idea)
    pillar="${2:-}"
    python3 "$SCRIPT_DIR/pick_idea.py" "$pillar"
    ;;

  stage)
    shift
    python3 "$SCRIPT_DIR/stage_post.py" "$@"
    ;;

  push)
    cd "$REPO_DIR"
    git add control.db posting/
    if git diff --cached --quiet; then
      echo "Nothing staged to push."
    else
      git commit -m "stage post(s) $(date -u +%Y-%m-%dT%H:%M:%SZ)"
      git push
      echo "OK pushed. GitHub Actions will send staged posts on its next daily run."
    fi
    ;;

  send-telegram)
    img="${2:?usage: daily.sh send-telegram <image_path> <caption text>}"
    shift 2
    caption="$*"
    python3 "$SENDERS_DIR/telegram_send.py" --photo "$img" "$caption"
    ;;

  send-bale)
    shift
    text="$*"
    python3 "$SENDERS_DIR/bale_send.py" "$text"
    ;;

  *)
    echo "Usage:"
    echo "  $0                 (interactive)"
    echo "  $0 idea [pillar]"
    echo "  $0 stage --platform telegram --date YYYY-MM-DD --text-file f [--image f] [--pillar p]"
    echo "  $0 push"
    echo "  $0 send-telegram <image_path> <caption text>"
    echo "  $0 send-bale <text>"
    exit 1
    ;;
esac
