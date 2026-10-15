#!/usr/bin/env python3
"""Rehearsal as a test: fail if any beat started more than LIMIT seconds after its planned time, or the talk overran.
Usage: python3 site/build/rehearsal_check.py rehearsal.json [limit_s=10]   (rehearsal.json is saved by the player's R key)"""
import json, sys
r = json.load(open(sys.argv[1])); limit = float(sys.argv[2]) if len(sys.argv) > 2 else 10
bad = 0
for b in r['beats']:
    d = b['actual_s'] - b['planned_s']; bad += d > limit
    print(f"{b['beat']:<12} planned {b['planned_s']:>6.1f}  actual {b['actual_s']:>6.1f}  drift {d:+6.1f}{'  LATE' if d > limit else ''}")
over = (r.get('total_actual_s') or 0) - (r.get('duration_s') or 0)
print(f"total {r.get('total_actual_s')} s for {r.get('duration_s')} s planned ({over:+.1f} s)")
sys.exit(1 if bad or over > limit else 0)
