#!/usr/bin/env python3
"""Check a talk narration (site/talk/narration/<persona>.json) against its timeline (site/talk/talk-10.json).

Every beat of the talk has paragraphs; each paragraph starts inside its beat, in order, and fits (read aloud at the
narration's words per minute) before the next paragraph or the end of the beat; each has the notes it was written from.
Usage: python3 site/build/narration_check.py [site/talk/narration/ceo.json ...]   (no arguments: every narration). Apache-2.0.
"""
import json, re, sys
from pathlib import Path

SITE = Path(__file__).resolve().parents[1]
talk = json.loads((SITE / 'talk/talk-10.json').read_text())
beats = {b['id']: b for b in talk['beats']}
order = [b['id'] for b in talk['beats']]

def words(s): return len(re.findall(r"[\w'’.-]+", re.sub(r'<[^>]+>', '', s)))

def check(path):
    n = json.loads(Path(path).read_text())
    errs, warn = [], []
    wps = n.get('words_per_minute', 150) / 60
    for k in ('persona', 'label', 'voice', 'beats'):
        if k not in n: errs.append(f'missing {k}')
    got = [b.get('id') for b in n.get('beats', [])]
    if got != order: errs.append(f'beats must be exactly, in order: {order}; got {got}')
    total = 0
    for b in n.get('beats', []):
        tb = beats.get(b.get('id'))
        if not tb: continue
        ps = b.get('paras') or []
        if not ps: errs.append(f"{b['id']}: no paragraphs")
        for i, p in enumerate(ps):
            at, text, notes = p.get('at'), p.get('text', ''), p.get('notes') or {}
            if not isinstance(at, (int, float)) or not 0 <= at < tb['dur']: errs.append(f"{b['id']}[{i}]: at {at} outside 0..{tb['dur']}")
            if i and isinstance(at, (int, float)) and at <= ps[i - 1].get('at', -1): errs.append(f"{b['id']}[{i}]: at must increase")
            if not text.strip(): errs.append(f"{b['id']}[{i}]: empty text")
            if not (notes.get('screen') and notes.get('from')): errs.append(f"{b['id']}[{i}]: notes need 'screen' and 'from'")
            end = ps[i + 1]['at'] if i + 1 < len(ps) else tb['dur']
            need = words(text) / wps
            total += words(text)
            if isinstance(at, (int, float)) and need > (end - at) + 0.5:
                errs.append(f"{b['id']}[{i}]: {words(text)} words need {need:.1f} s read aloud, the slot is {end - at:.1f} s")
    return errs, warn, total

paths = sys.argv[1:] or sorted(str(p) for p in (SITE / 'talk/narration').glob('*.json') if p.name not in ('index.json', 'beats.json'))
bad = 0
for p in paths:
    e, w, total = check(p)
    print(f"{p}: {'ok' if not e else f'{len(e)} problem(s)'} · {total} words")
    for x in e: print('  ' + x)
    bad += bool(e)
sys.exit(1 if bad else 0)
