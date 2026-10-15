#!/usr/bin/env bash
# Post one message on a role's lane in the studio bus vault, timed. Only the role itself writes its lane.
# Usage: VAULT_DIR=.vault-bus SGIT_TOKEN=... bash lane.sh <from-role> <to-role> <message-json-file> [trace.jsonl]
# Not yet run against a server (run 1 had no sgit credentials): check `sgit write --help` first.
# The bus vault must already be cloned into $VAULT_DIR (key via stdin: printf '%s' "$VAULT_KEY" | sgit clone - .vault-bus).
set -euo pipefail
FROM=$1; TO=$2; MSG=$3; TRACE=${4:-trace.jsonl}; VDIR=${VAULT_DIR:-.vault-bus}
SEQ=$(cd "$VDIR" && sgit ls 2>/dev/null | grep -c "lanes/$FROM/" || true); SEQ=$(printf %04d $((SEQ + 1)))
DEST="lanes/$FROM/$SEQ-to-$TO.json"; MSGP=$(realpath "$MSG"); t0=$(date +%s%3N)
( cd "$VDIR" && sgit ${SGIT_TOKEN:+--token "$SGIT_TOKEN"} write "$DEST" --file "$MSGP" --message "$FROM -> $TO #$SEQ" --push --json ) > /dev/null   # global --token goes before the subcommand
t1=$(date +%s%3N)
printf '{"kind":"lane","from":"%s","to":"%s","path":"%s","bytes":%s,"start_ms":%s,"ms":%s}\n' "$FROM" "$TO" "$DEST" "$(wc -c < "$MSG")" $t0 $((t1 - t0)) >> "$TRACE"
echo "$DEST"
