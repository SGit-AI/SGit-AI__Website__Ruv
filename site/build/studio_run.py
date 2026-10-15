#!/usr/bin/env python3
"""Write site/studio/run.json, the studio page's run record: the hive trace (from out/poc7/trace.jsonl, else evidence/poc7-trace.jsonl),
and per version its sha256, size, video and poster. Usage: python3 site/build/studio_run.py"""
import hashlib, json, pathlib, re, shutil
ROOT = pathlib.Path(__file__).resolve().parents[2]; SITE = ROOT / 'site'; ST = SITE / 'studio'
src = ROOT / 'out/poc7/trace.jsonl'
if src.exists(): shutil.copy(src, ROOT / 'evidence/poc7-trace.jsonl')
trace = [json.loads(l) for l in (ROOT / 'evidence/poc7-trace.jsonl').read_text().splitlines() if l.strip()]
spec = json.loads((ROOT / 'poc/poc7-studio/spec.json').read_text())
versions = []
for v in spec['versions']:
    f = ST / v['id'] / 'index.html'
    if not f.exists(): continue
    b = f.read_bytes()
    versions.append({**v, 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest(),
                     'video': f"video/{v['id']}.mp4" if (ST / 'video' / f"{v['id']}.mp4").exists() else None,
                     'poster': f"posters/{v['id']}.webp" if (ST / 'posters' / f"{v['id']}.webp").exists() else None})
hive = {'workers': sum(1 for t in trace if 'hive-mind spawn' in t['cmd'] and t['rc'] == 0),
        'tasks': sum(1 for t in trace if 'hive-mind task' in t['cmd'] and t['rc'] == 0)}
builders = json.loads((ROOT / 'evidence/poc7-builders.json').read_text())
state = json.loads((ROOT / 'evidence/poc7-hive-state.json').read_text())
delivered = [m['message'] for m in state['sharedMemory'].get('broadcasts', []) if m['message'].startswith('delivered ')]
json.dump({'builders': builders, 'delivered': delivered, 'run': 'studio run 1', 'date': '2026-10-15', 'ruflo': '3.56.10', 'hive': hive, 'versions': versions, 'trace': trace},
          open(ST / 'run.json', 'w'), indent=1)
print('studio/run.json:', len(trace), 'calls,', len(versions), 'versions,', hive)
