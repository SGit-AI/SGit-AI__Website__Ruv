#!/usr/bin/env bash
# Close a studio run: record each delivered version (sha256, bytes) in the hive's memory, then pack the run folder
# that becomes the run vault (brief, versions, videos, trace, hive status). Every ruflo call is timed into the trace.
# Usage: bash poc/poc7-studio/close.sh <out-dir>   (after hive.sh <out-dir>; run from the repo root)
set -uo pipefail
OUT=$(realpath -m "${1:-out/poc7}"); RUFLO="$(pwd)/node_modules/.bin/ruflo"; ROOT=$(pwd)
n=$(wc -l < "$OUT/trace.jsonl")
run() { local actor=$1; shift; n=$((n+1)); local t0=$(date +%s%3N)
  ( cd "$(cat "$OUT/workdir")" && "$RUFLO" "$@" ) > "$OUT/log/$(printf %02d $n).txt" 2>&1; local rc=$?; local t1=$(date +%s%3N)
  python3 -c 'import json,sys; print(json.dumps({"seq":int(sys.argv[1]),"actor":sys.argv[2],"cmd":" ".join(sys.argv[6:]),"rc":int(sys.argv[3]),"start_ms":int(sys.argv[4]),"ms":int(sys.argv[5])-int(sys.argv[4])}))' \
    $n "$actor" $rc $t0 $t1 "$@" >> "$OUT/trace.jsonl"; }
for f in site/studio/v*/index.html; do
  id=$(basename "$(dirname "$f")"); sum=$(sha256sum "$f" | cut -c1-16); bytes=$(wc -c < "$f")
  run developer hive-mind broadcast -m "delivered studio/$id sha256:$sum bytes:$bytes" -f developer   # memory -a set did not persist across calls in 3.56.10; broadcasts do
done
run historian hive-mind memory -a list
python3 -c "import json,sys; s=json.load(open(sys.argv[1])); b=[m['message'] for m in s['sharedMemory'].get('broadcasts',[])]; d=[m for m in b if m.startswith('delivered ')]; print(len(d),'deliveries in the hive state'); [print(' ',m) for m in d]" "$(cat "$OUT/workdir")/.claude-flow/hive-mind/state.json" | tee "$OUT/log/deliveries.txt"
python3 -c "import json,sys; s=json.load(open(sys.argv[1])); s.pop('hiveToken',None); json.dump(s,open(sys.argv[2],'w'),indent=1)" "$(cat "$OUT/workdir")/.claude-flow/hive-mind/state.json" "$OUT/hive-state.json"   # the hive token stays local
run queen hive-mind status
run queen daemon stop
R="$OUT/run"; rm -rf "$R" && mkdir -p "$R/brief" "$R/versions" "$R/trace" "$R/video"
cp poc/poc7-studio/spec.json site/data/report.json site/data/abp.json "$R/brief/"
cp -R site/studio/v* "$R/versions/"; cp "$OUT/trace.jsonl" "$OUT/hive-state.json" "$R/trace/"; cp -R "$OUT/log" "$R/trace/ruflo-log"
cp site/studio/video/*.mp4 "$R/video/" 2>/dev/null || true
echo "run folder: $R  ($(find "$R" -type f | wc -l) files). To keep it: VAULT_KEY=... SGIT_TOKEN=... scripts/vault_write.sh $R runs/<id> 'studio run'"
