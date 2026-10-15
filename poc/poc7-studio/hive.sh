#!/usr/bin/env bash
# POC7 studio: a Ruflo hive-mind (queen + role workers) holds the plan for the animation studio.
# Every ruflo call is timed and logged to $OUT/trace.jsonl (observability); its stdout goes to $OUT/log/.
# Usage: bash poc/poc7-studio/hive.sh <out-dir>   (run from the repo root; npm ci first)
set -uo pipefail
OUT=$(realpath -m "${1:-out/poc7}"); RUFLO="$(pwd)/node_modules/.bin/ruflo"; SPEC="$(pwd)/poc/poc7-studio/spec.json"
# A fresh work folder per run: Ruflo anchors each project's policy ledger outside the project (~/.config/ruflo/policy-trust/),
# so a deleted-and-recreated folder at the same path is refused with policy-anchor-log-missing (its tamper check; do not remove the anchor).
WORK="$OUT/work-$(date +%s)"; mkdir -p "$OUT/log" "$WORK" && echo "$WORK" > "$OUT/workdir" && cd "$WORK"
: > "$OUT/trace.jsonl"; n=0
run() {  # run <actor> <ruflo args...>: time it, keep its output, append one trace line
  local actor=$1; shift; n=$((n+1)); local t0=$(date +%s%3N)
  "$RUFLO" "$@" > "$OUT/log/$(printf %02d $n).txt" 2>&1; local rc=$?; local t1=$(date +%s%3N)
  python3 -c 'import json,sys; print(json.dumps({"seq":int(sys.argv[1]),"actor":sys.argv[2],"cmd":" ".join(sys.argv[6:]),"rc":int(sys.argv[3]),"start_ms":int(sys.argv[4]),"ms":int(sys.argv[5])-int(sys.argv[4])}))' \
    $n "$actor" $rc $t0 $t1 "$@" >> "$OUT/trace.jsonl"
}
run queen hive-mind init -t hierarchical-mesh -c byzantine -m 12
for role in $(python3 -c "import json;print(' '.join(r['id'] for r in json.load(open('$SPEC'))['roles']))"); do
  run queen hive-mind spawn -n 1 -t "$role" -r specialist -p "$role"
done
while IFS=$'\t' read -r id title; do    # process substitution, not a pipe: the counter must survive the loop
  run conductor hive-mind task -d "$id: $title" -p high
done < <(python3 -c "import json;[print(v['id']+'\t'+v['title']) for v in json.load(open('$SPEC'))['versions']]")
run conductor hive-mind broadcast -m "Brief: animate how an ABP + sgit vaults make a Ruflo swarm trustworthy; one HTML file per version; data from site/data only" -f conductor
run librarian hive-mind memory -a set -k studio/spec -v "poc/poc7-studio/spec.json"   # prints OK; does not persist across CLI calls in 3.56.10 (kept to show it)
run queen hive-mind status
run queen swarm status
run queen daemon stop
echo "trace: $OUT/trace.jsonl ($n ruflo calls)"
