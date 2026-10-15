#!/usr/bin/env python3
"""Generate the site's infographics through OpenRouter (image-output chat models).
Usage: OPENROUTER_API_KEY=... python3 site/build/gen_infographics.py [--only id,id] [--force]
Reads site/build/infographics.json, writes site/assets/img/<id>.png and site/build/infographics-log.json
(model, duration, cost per image). Model per job follows newsroom.sgit.ai's bake-off: labelled diagrams ->
Gemini 3 Pro Image; concept slides and comparisons -> Nano Banana 2.1, falling back to Gemini 2.5 Flash Image
when a model is rate-limited upstream."""
import json, os, sys, time, base64, subprocess, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
SPEC = json.load(open(ROOT / 'site/build/infographics.json'))
OUT = ROOT / 'site/assets/img'; OUT.mkdir(parents=True, exist_ok=True)
LOG = ROOT / 'site/build/infographics-log.json'
KEY = os.environ.get('OPENROUTER_API_KEY') or sys.exit('OPENROUTER_API_KEY not set')
MODELS = {
    'diagram':    ['google/gemini-3-pro-image', 'google/gemini-2.5-flash-image'],
    'concept':    ['google/gemini-nano-banana-2.1', 'google/gemini-2.5-flash-image'],
    'comparison': ['google/gemini-nano-banana-2.1', 'google/gemini-3-pro-image', 'google/gemini-2.5-flash-image'],
}
only = set(); force = '--force' in sys.argv
if '--only' in sys.argv: only = set(sys.argv[sys.argv.index('--only') + 1].split(','))
log = json.load(open(LOG)) if LOG.exists() else {}
def call(model, prompt):
    body = {'model': model, 'modalities': ['image', 'text'], 'messages': [{'role': 'user', 'content': prompt}]}
    t = time.time()
    r = subprocess.run(['curl', '-sS', '--max-time', '240', 'https://openrouter.ai/api/v1/chat/completions',
                        '-H', f'Authorization: Bearer {KEY}', '-H', 'Content-Type: application/json', '-d', json.dumps(body)],
                       capture_output=True, text=True)
    d = json.loads(r.stdout or '{}')
    return d, round(time.time() - t, 1)
for img in SPEC['images']:
    if only and img['id'] not in only: continue
    png = OUT / f"{img['id']}.png"
    if png.exists() and not force: print('skip', img['id']); continue
    prompt = f"{img['prompt']}\n{SPEC['style']}"
    for model in MODELS[img['kind']]:
        d, dur = call(model, prompt)
        if 'error' in d: print(img['id'], model, 'ERR', str(d['error'])[:120]); time.sleep(3); continue
        imgs = d.get('choices', [{}])[0].get('message', {}).get('images') or []
        if not imgs: print(img['id'], model, 'no image returned'); continue
        url = imgs[0]['image_url']['url']
        png.write_bytes(base64.b64decode(url.split(',', 1)[1]))
        log[img['id']] = {'model': model, 'duration_s': dur, 'cost_usd': d.get('usage', {}).get('cost'), 'generation_id': d.get('id'), 'at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
        print(img['id'], model, f'{dur}s', '$%.4f' % (log[img['id']]['cost_usd'] or 0), png.stat().st_size, 'bytes')
        break
    json.dump(log, open(LOG, 'w'), indent=2)
total = sum((v.get('cost_usd') or 0) for v in log.values())
print(f'total so far: ${total:.2f} for {len(log)} images')
