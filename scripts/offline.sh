#!/usr/bin/env bash
# ruv.sgit.ai on a laptop, with no network.
#
#   bash scripts/offline.sh setup    once, ONLINE: npm ci (Ruflo, RuVector, MetaHarness, pinned) and a Python venv
#                                    in .venv (sgit-ai, the SG/Send vault server). After this the network is not used.
#   bash scripts/offline.sh all      OFFLINE: doctor, pocs, run, then serve
#   bash scripts/offline.sh doctor   check every piece is installed
#   bash scripts/offline.sh pocs     POC1, POC3, POC4, POC5, then sync the site and validate it
#   bash scripts/offline.sh run      one ruv.sgit run: a Ruflo hive + an ephemeral sgit vault on a local vault server;
#                                    the workers are the POC scripts; open, deliver, close (measure), delete
#   bash scripts/offline.sh serve    the site at http://localhost:8080 (PORT=... to change)
#
# The laptop run's ledger and evidence go to out/offline/ (git-ignored), not to the public ledger in site/data/.
# Its keys and server token live in ~/.ruv-sgit-offline (mode 0600) and are never printed.
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT=$(pwd)
VENV="$ROOT/.venv"
OFF="$ROOT/out/offline"
export RUVSGIT_HOME="${RUVSGIT_HOME:-$HOME/.ruv-sgit-offline}"
export RUVSGIT_PORT="${RUVSGIT_PORT:-8091}"            # the site uses 8080
export RUVSGIT_SGIT="$VENV/bin/sgit"
export RUVSGIT_SERVER_PY="$VENV/bin/python"
export RUVSGIT_LEDGER="$OFF/vaults.json"
export RUVSGIT_EVIDENCE="$OFF/evidence"
PORT="${PORT:-8080}"

say() { printf '\n== %s\n' "$*"; }
die() { printf 'offline: %s\n' "$*" >&2; exit 1; }

setup() {
  say "setup (needs the network, once)"
  command -v node >/dev/null || die "node 20+ is needed"
  command -v python3 >/dev/null || die "python 3.11+ is needed"
  npm ci --no-audit --no-fund
  [ -x "$VENV/bin/python" ] || python3 -m venv "$VENV"
  "$VENV/bin/pip" install --quiet --upgrade pip
  "$VENV/bin/pip" install --quiet "sgit-ai==0.21.0" "sgraph-ai-app-send==0.34.0" "mcp<2"
  doctor
  say "set up: from here on 'bash scripts/offline.sh all' needs no network"
}

doctor() {
  say "doctor"
  local ok=1
  check() { if eval "$2" >/dev/null 2>&1; then printf '  ok   %s\n' "$1"; else printf '  MISSING  %s  (%s)\n' "$1" "$3"; ok=0; fi; }
  check "node $(node --version 2>/dev/null)"        'node -e "process.exit(+process.versions.node.split(\".\")[0] >= 20 ? 0 : 1)"' "install Node 20+"
  check "python3 $(python3 --version 2>/dev/null | cut -d" " -f2)" 'python3 -c "import sys; sys.exit(sys.version_info < (3, 11))"' "install Python 3.11+"
  check "ruflo 3.56.10"                    '[ "$(node -p "require(\"./node_modules/ruflo/package.json\").version")" = 3.56.10 ]' "run setup"
  check "@ruvector/wasm 0.2.1"             '[ -f node_modules/@ruvector/wasm/pkg/ruvector_wasm_bg.wasm ]' "run setup"
  check "metaharness 0.4.17"               '[ "$(node -p "require(\"./node_modules/metaharness/package.json\").version")" = 0.4.17 ]' "run setup"
  check "sgit-ai 0.21.0 (.venv)"           '"$VENV/bin/python" -c "import importlib.metadata as m; assert m.version(\"sgit-ai\") == \"0.21.0\""' "run setup"
  check "SG/Send vault server 0.34.0 (.venv)" '"$VENV/bin/python" -c "import importlib.metadata as m, sgraph_ai_app_send__docker; assert m.version(\"sgraph-ai-app-send\") == \"0.34.0\""' "run setup"
  check "site/vendor (mermaid, three.js, marked)" '[ -s site/vendor/mermaid-11.12.0.min.js ] && [ -s site/vendor/three.js-r128.min.js ] && [ -s site/vendor/marked-15.0.7.min.js ]' "in the repository; git checkout site/vendor"
  [ "$ok" = 1 ] || die "missing pieces above"
}

pocs() {
  say "POCs (no network)"
  npm run --silent abp:gate
  npm run --silent poc1
  npm run --silent poc3
  npm run --silent poc4:build
  npm run --silent poc5
  npm run --silent cleanup >/dev/null 2>&1 || true
  say "site: sync POC outputs into the site, build, validate"
  bash site/build/sync.sh >/dev/null
  python3 site/build/validate.py
}

run() {
  say "a ruv.sgit run on this laptop (vault server on 127.0.0.1:$RUVSGIT_PORT)"
  [ -f out/poc1/report.json ] && [ -d out/poc3 ] && [ -d out/app ] || die "run 'pocs' first: the workers deliver its outputs"
  local R="laptop-$(date -u +%Y%m%d-%H%M%S)" W="$OFF/workers-$$.json" t0
  mkdir -p "$OFF"
  local py="python3 poc/ruv-sgit/ruvsgit.py"
  $py server-stop >/dev/null 2>&1 || true
  $py server-start
  trap '$py server-stop >/dev/null 2>&1 || true' EXIT
  $py open "$R" poc/ruv-sgit/runs/laptop.spec.json
  echo '[' > "$W"; local sep=''
  for w in policy:policy:out/poc1 rights:rights:out/poc3 app:app:out/app; do
    IFS=: read -r id role src <<< "$w"
    t0=$(date +%s); $py deliver "$R" "$id" "$role" "$src"
    printf '%s{"id": "%s", "role": "%s", "kind": "script (no model)", "tokens": 0, "wall_s": %s}\n' "$sep" "$id" "$role" "$(( $(date +%s) - t0 ))" >> "$W"; sep=','
  done
  echo ']' >> "$W"
  $py close "$R" "$W"
  $py delete "$R"
  $py server-stop
  trap - EXIT
  say "ledger: $RUVSGIT_LEDGER · evidence: $RUVSGIT_EVIDENCE/$R.json"
}

serve() {
  say "the site at http://localhost:$PORT  (Ctrl-C to stop; the talk works from talk/offline-10.html too)"
  exec python3 -m http.server -b 127.0.0.1 -d site "$PORT"
}

case "${1:-}" in
  setup) setup ;;
  doctor) doctor ;;
  pocs) doctor; pocs ;;
  run) doctor; run ;;
  serve) serve ;;
  all) doctor; pocs; run; serve ;;
  *) sed -n '2,14p' "$0" | sed 's/^# \{0,1\}//'; exit 1 ;;
esac
