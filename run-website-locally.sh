#!/usr/bin/env bash
# Run ruv.sgit.ai on this machine. No setup, no network: Python 3 only.
#
#   ./run-website-locally.sh          the site at http://localhost:8080
#   ./run-website-locally.sh 9000     on another port
#
# Then open:
#   http://localhost:PORT/                                     the site
#   http://localhost:PORT/talk/player.html?talk=talk-10.json   tonight's talk (the player)
# No server at all: open site/talk/offline-10.html from the file (live slides show as screenshots).
# Everything else (the POCs, a ruv.sgit run on a local vault server): bash scripts/offline.sh (see README).
set -euo pipefail
cd "$(dirname "$0")"
PORT="${1:-${PORT:-8080}}"
command -v python3 >/dev/null || { echo "python3 is needed" >&2; exit 1; }
URL="http://localhost:$PORT"
echo "ruv.sgit.ai: $URL"
echo "the talk:    $URL/talk/player.html?talk=talk-10.json"
echo "(Ctrl-C to stop)"
( sleep 1; { command -v open >/dev/null && open "$URL/talk/player.html?talk=talk-10.json"; } || { command -v xdg-open >/dev/null && xdg-open "$URL/talk/player.html?talk=talk-10.json"; } || true ) >/dev/null 2>&1 &
exec python3 -m http.server -b 127.0.0.1 -d site "$PORT"
