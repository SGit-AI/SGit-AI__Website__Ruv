#!/usr/bin/env bash
# Write a local folder into an sgit vault path and push. Keys/tokens come from env only.
# Usage: VAULT_KEY=... SGIT_TOKEN=... scripts/vault_write.sh <local_dir> <vault_path_prefix> "<message>" [vault_dir]
set -euo pipefail
SRC="$1"; PREFIX="$2"; MSG="$3"; VDIR="${4:-.vault-work}"
[ -n "${VAULT_KEY:-}" ] || { echo "VAULT_KEY not set" >&2; exit 2; }
if [ ! -d "$VDIR/.sg_vault" ]; then
  printf '%s' "$VAULT_KEY" | sgit clone ${SGIT_TOKEN:+--token "$SGIT_TOKEN"} - "$VDIR" >/dev/null   # key via stdin, never argv
fi
mkdir -p "$VDIR/$PREFIX" && cp -R "$SRC"/. "$VDIR/$PREFIX/"
( cd "$VDIR" && sgit pull >/dev/null 2>&1 || true; sgit commit -m "$MSG" && sgit push ${SGIT_TOKEN:+--token "$SGIT_TOKEN"} )
( cd "$VDIR" && sgit history log --oneline -n 3 )
