#!/usr/bin/env bash
# Copy POC outputs (out/) and recorded evidence (evidence/) into the site, so pages render real numbers.
# Usage: bash site/build/sync.sh   (run after npm run poc1 poc3 poc4:build poc5)
set -euo pipefail
cd "$(dirname "$0")/../.."
mkdir -p site/data site/app
cp out/poc1/report.json site/data/report.json 2>/dev/null || cp evidence/poc1-report.json site/data/report.json 2>/dev/null || true
cp out/poc1/rules.json site/data/rules.json 2>/dev/null || true
cp out/poc1/state-abp.json site/data/state-abp.json 2>/dev/null || true
cp abp/examples/ruflo-sparc-swarm.abp.json site/data/abp.json
cp out/poc3/rvm-caps.md site/data/rvm-caps.md 2>/dev/null || cp evidence/poc3-rvm-caps.md site/data/rvm-caps.md
cp out/poc5/diff.md site/data/poc5-diff.md 2>/dev/null || cp evidence/poc5-diff.md site/data/poc5-diff.md 2>/dev/null || true
cp out/poc5/score.json site/data/score.json 2>/dev/null || cp evidence/poc5-score.json site/data/score.json 2>/dev/null || true
cp evidence/poc2-run.txt site/data/poc2-run.txt 2>/dev/null || true
cp evidence/poc2-history.json site/data/poc2-history.json 2>/dev/null || true
cp evidence/notes.md site/data/notes.md
if [ -d out/app ]; then rm -rf site/app && cp -R out/app site/app; fi
echo "site/data:" && ls site/data && echo "site/app:" && ls site/app
python3 site/build/talk_offline.py
