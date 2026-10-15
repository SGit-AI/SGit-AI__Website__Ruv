#!/usr/bin/env bash
# POC2: Ruflo agent memory, per role, kept in an sgit vault (branch per role, merged), then restored on a fresh runner.
# Phase A (writer):  ROLE=coder bash run.sh write
# Phase B (reader):  bash run.sh read     (fresh machine: clone vault, restore DB files, query)
# Env: VAULT_KEY (memory vault), SGIT_TOKEN. Requires npm ci WITH install scripts (better-sqlite3 native), see evidence/notes.md
set -euo pipefail
RUFLO="npx --no-install ruflo"
MODE="${1:-write}"; ROLE="${ROLE:-coder}"; RUN="${RUN_ID:-local-$(date +%s)}"
VDIR=.vault-memory; MAIN="${MAIN_BRANCH:-current}"   # sgit names the default branch "current" (verified: sgit branch list)
clone() { [ -d "$VDIR/.sg_vault" ] || printf '%s' "$VAULT_KEY" | sgit clone ${SGIT_TOKEN:+--token "$SGIT_TOKEN"} - "$VDIR" >/dev/null; }
cleanup() { $RUFLO daemon stop >/dev/null 2>&1 || true; }
trap cleanup EXIT
if [ "$MODE" = write ]; then
  W=work-$ROLE && rm -rf $W && mkdir $W && cd $W
  $RUFLO memory init --verify false >/dev/null
  $RUFLO memory store -k "$ROLE/lesson-$RUN" --value "run $RUN: legacy policy allowed email.send; ABP denied it" -n "$ROLE" --no-embedding --provenance agent_output
  $RUFLO memory list -n "$ROLE" > memory-list.txt
  cd ..; clone
  ( cd "$VDIR" && sgit pull >/dev/null 2>&1 || true; sgit branch new "mem-$ROLE-$RUN" >/dev/null )
  mkdir -p "$VDIR/memory/$ROLE"
  # the durable stores (export/import were unreliable in 3.56.10; see evidence/notes.md)
  for f in .swarm/memory.db .swarm/agentdb-memory.db .claude/memory.db ruvector.db memory-list.txt; do
    [ -f "$W/$f" ] && mkdir -p "$VDIR/memory/$ROLE/$(dirname $f)" && cp "$W/$f" "$VDIR/memory/$ROLE/$f"; done
  ( cd "$VDIR" && sgit commit -m "memory: $ROLE learned something in run $RUN" && sgit push ${SGIT_TOKEN:+--token "$SGIT_TOKEN"} \
      && sgit branch switch "$MAIN" && sgit branch merge "mem-$ROLE-$RUN" && sgit push ${SGIT_TOKEN:+--token "$SGIT_TOKEN"} )
  ( cd "$VDIR" && sgit history log --json -n 5 ) > history-$ROLE.json
else
  clone; ( cd "$VDIR" && sgit pull >/dev/null 2>&1 || true )
  for ROLE_DIR in "$VDIR"/memory/*/; do R=$(basename "$ROLE_DIR"); W=restore-$R; rm -rf $W && mkdir $W
    cp -R "$ROLE_DIR". "$W/"; ( cd $W && echo "== $R" && $RUFLO memory list -n "$R" ); done
  ( cd "$VDIR" && sgit history log --oneline -n 20 )
fi
