#!/usr/bin/env python3
"""The numbers in the article "How it was made" (site/articles/src/how-it-was-made.md), computed from the records.

Sources, all in this repository unless named:
  git log (commits, times, sessions) · site/admin/versions.json (releases) · site/data/vaults.json (the ruv.sgit ledger)
  poc/ruv-sgit/runs/*.spec.json (run specs) · evidence/poc7-trace.jsonl + poc7-builders.json (studio run 1)
  site/talk/talk-10.json + site/talk/player.html (slides, player controls) · site/**/*.html (pages)
  All repository files are read as they were at BASELINE (git show), so the numbers do not move as later runs land.
  --messages PATH: Dinis's messages to the session, exported with timestamps (not in the repository; without it,
  the message counts already in the output file are kept).

Output: site/data/how-it-was-made-stats.json (counts up to BASELINE, the r10-articles spec commit).  Usage: python3 site/build/history_stats.py [--messages user-messages.md]
Apache-2.0."""
import json, pathlib, re, subprocess, sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[2]
SITE = ROOT / 'site'
OUT = SITE / 'data' / 'how-it-was-made-stats.json'
# Counted up to the commit that started run r10-articles (the run that wrote the article), so later commits do not move the numbers.
BASELINE = '76fa67a'
# The talk was on the evening of 15 Oct (his slot: 7 pm London, BST = UTC+1). His last pre-talk message is at 18:08 UTC and the
# last pre-talk commit at 18:09 UTC; nothing was committed or sent between then and 22:08 UTC. 19:00 UTC splits before/after.
TALK_START_UTC = '2026-10-15T19:00'


def blob(rel):
    """a file's text as it was at BASELINE (path relative to the repository root)"""
    r = subprocess.run(['git', '-C', str(ROOT), 'show', f'{BASELINE}:{rel}'], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def ts(s):
    return datetime.fromisoformat(s.replace('Z', '+00:00')).astimezone(timezone.utc)


def git_commits():
    fmt = '%h%x1f%ct%x1f%an%x1f%s%x1f%(trailers:key=Claude-Session,valueonly,separator=%x2C)%x1e'
    raw = subprocess.run(['git', '-C', str(ROOT), 'log', '--reverse', f'--format={fmt}', BASELINE], capture_output=True, text=True, check=True).stdout
    out = []
    for rec in raw.split('\x1e'):
        rec = rec.strip('\n')
        if not rec: continue
        h, ct, an, subj, sess = rec.split('\x1f')
        out.append({'hash': h, 'utc': datetime.fromtimestamp(int(ct), timezone.utc), 'author': an, 'subject': subj,
                    'session': sess.strip().rsplit('/', 1)[-1] or None})
    return out


def messages(path):
    """Dinis's own messages. Rule: a timestamped section counts unless it is system or agent text:
    'Stop hook feedback' (a git hook), 'Another Claude session sent a message' (a subagent's report),
    '[context compacted' (the session's summary), '<task-notification' (a background job), 'Base directory for
    this skill' (a skill's text loaded into the session). '[Image: source: ...]' sections are the screenshots
    attached to the message just before them: they are counted as images, not as messages."""
    text = pathlib.Path(path).read_text(encoding='utf-8')
    secs = re.split(r'^## (\d{4}-\d\d-\d\dT\d\d:\d\d)\s*$', text, flags=re.M)
    excluded = {'stop-hook': 0, 'agent-report': 0, 'compaction': 0, 'task-notification': 0, 'skill-text': 0}
    msgs, images = [], 0
    for i in range(1, len(secs), 2):
        t, body = secs[i], secs[i + 1].strip()
        if body.startswith('Stop hook feedback'): excluded['stop-hook'] += 1; continue
        if body.startswith('Another Claude session sent a message') or '<agent-message' in body[:200]: excluded['agent-report'] += 1; continue
        if body.startswith('[context compacted'): excluded['compaction'] += 1; continue
        if body.startswith('<task-notification'): excluded['task-notification'] += 1; continue
        if body.startswith('Base directory for this skill'): excluded['skill-text'] += 1; continue
        if body.startswith('[Image: source:'): images += body.count('[Image: source:'); continue
        msgs.append({'utc': ts(t + ':00+00:00'), 'words': len(body.split()), 'has_image': '[image attached]' in body})
    return msgs, images, excluded


def main():
    args = sys.argv[1:]
    mpath = args[args.index('--messages') + 1] if '--messages' in args else None
    prev = json.loads(OUT.read_text()) if OUT.exists() else {}

    commits = git_commits()
    talk = ts(TALK_START_UTC + ':00+00:00')
    first, last = commits[0], commits[-1]
    pre = [c for c in commits if c['utc'] < talk]
    sessions = {}
    for c in commits:
        if c['session']: sessions.setdefault(c['session'], []).append(c['hash'])

    vers = json.loads(blob('site/admin/versions.json'))['releases']
    led = json.loads(blob('site/data/vaults.json'))['vaults']
    runs = []
    for v in led:
        model_workers = [w for w in v['workers'] if w.get('tokens')]
        probe = int(re.match(r'(\d+)', v['server_store']['probe']).group(1))
        runs.append({'run': v['run'], 'created_utc': v['created_at'], 'deleted_utc': v.get('deleted_at'),
                     'minutes_open_to_delete': round((ts(v['deleted_at']) - ts(v['created_at'])).total_seconds() / 60, 1),
                     'hive_workers': v['hive']['workers'], 'ruflo_calls': v['hive']['ruflo_calls'],
                     'worker_entries': len(v['workers']), 'model_workers': len(model_workers),
                     'conductor_entries': sum(1 for w in v['workers'] if w['role'] == 'conductor'),
                     'roles': sorted({w['role'] for w in v['workers']}),
                     'tokens': sum(w['tokens'] for w in model_workers), 'tool_uses': sum(w.get('tool_uses') or 0 for w in v['workers']),
                     'branches': len(v['branches']), 'commits': v['commits'],
                     'files_delivered': v.get('files_delivered'), 'bytes_delivered': v.get('bytes_delivered'),
                     'files_in_vault': v['files'], 'bytes_plain': v['bytes_plain'],
                     'server_files': v['server_store']['files'], 'server_bytes': v['server_store']['bytes'],
                     'fragments_probed': probe, 'plaintext_hits': v['server_store']['plaintext_hits'],
                     'clone_identical': v['clone']['identical'], 'clone_files': v['clone']['files'],
                     'deleted': bool(v.get('deleted_at')),
                     'delete_verified': (v.get('delete_check') or {}).get('store_paths_left') == 0 and (v.get('delete_check') or {}).get('clone_after_delete') == 'failed'})
    real = [r for r in runs if r['run'] != 'smoke-1']
    specs = sorted(p.stem.replace('.spec', '') for p in (ROOT / 'poc' / 'ruv-sgit' / 'runs').glob('*.spec.json'))

    trace = [json.loads(l) for l in blob('evidence/poc7-trace.jsonl').splitlines() if l.strip()]
    builders = json.loads(blob('evidence/poc7-builders.json'))

    talk_j = json.loads(blob('site/talk/talk-10.json'))
    beats, extras = talk_j['beats'], talk_j.get('extras', [])
    def page_of(b):
        src = (b.get('slide') or {}).get('src')
        return blob((SITE / 'talk' / src).resolve().relative_to(ROOT).as_posix()) if src else None
    live = [b for b in beats if (b.get('slide') or {}).get('layout') == 'iframe']
    on_clock = [b for b in live if 'clock.js' in (page_of(b) or '')]
    with_steps = [b for b in live if 'RUV_STEPS' in (page_of(b) or '')]

    player = blob('site/talk/player.html')
    onkey = player[player.index('function onKey'):]
    onkey = onkey[:onkey.index('\n}\n')]
    literals = sorted(set(re.findall(r"k === '([^']+)'", onkey)))
    synthetic = {'tap', 'swipe-next', 'swipe-back', 'reset-timer'}
    keys = [k for k in literals if k not in synthetic]
    keys_folded = sorted({k.lower() for k in keys})
    actions = len(re.findall(r'(?:^|else )if \(k ===', onkey, flags=re.M))   # one branch per action in onKey
    buttons = re.findall(r'<button[^>]*data-k="([^"]*)"', player)
    params = sorted(set(re.findall(r"qs\.(?:get|has)\('([a-z]+)'\)", player)))
    rates = json.loads(re.search(r'const RATES = (\[[^\]]*\])', player).group(1))

    tree = subprocess.run(['git', '-C', str(ROOT), 'ls-tree', '-r', '--name-only', BASELINE, 'site'], capture_output=True, text=True, check=True).stdout.split()
    pages = sorted(t[5:] for t in tree if t.endswith('.html') and '/vendor/' not in t)
    art_src = sorted(t.rsplit('/', 1)[1][:-3] for t in tree if t.startswith('site/articles/src/') and t.endswith('.md'))

    out = {
        'generated_by': 'site/build/history_stats.py', 'generated_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'commits': {'total': len(commits), 'before_talk': len(pre), 'first': {'hash': first['hash'], 'utc': first['utc'].isoformat()},
                    'last': {'hash': last['hash'], 'utc': last['utc'].isoformat(), 'subject': last['subject']},
                    'last_before_talk': {'hash': pre[-1]['hash'], 'utc': pre[-1]['utc'].isoformat()},
                    'hours_first_to_last': round((last['utc'] - first['utc']).total_seconds() / 3600, 1),
                    'hours_first_to_last_before_talk': round((pre[-1]['utc'] - first['utc']).total_seconds() / 3600, 1),
                    'by_session': {s: len(h) for s, h in sessions.items()},
                    'by_dinis_without_session': sum(1 for c in commits if not c['session']),
                    'ruv_sgit_run_commits': sum(1 for c in commits if re.search(r'\br\d+-|ruv\.sgit run|smoke-1', c['subject']))},
        'releases': {'total': len(vers), 'first': vers[-1]['version'], 'last': vers[0]['version']},
        'studio_run_1': {'ruflo_calls': len(trace), 'ruflo_failed': sum(1 for t in trace if t.get('rc', 0) != 0),
                         'ruflo_seconds': round(sum(t.get('ms', 0) for t in trace) / 1000, 1),
                         'builder_tokens': sum(b.get('tokens', 0) for b in (builders if isinstance(builders, list) else builders.get('builders', []))),
                         'versions': 7},
        'ruv_sgit': {'runs_in_ledger': len(runs), 'runs_excluding_smoke': len(real), 'run_specs': specs,
                     'worker_entries_total': sum(r['worker_entries'] for r in runs),
                     'model_workers_total': sum(r['model_workers'] for r in runs),
                     'conductor_entries_total': sum(r['conductor_entries'] for r in runs),
                     'hive_workers_total': sum(r['hive_workers'] for r in runs),
                     'ruflo_calls_total': sum(r['ruflo_calls'] for r in runs),
                     'worker_tokens_total': sum(r['tokens'] for r in runs),
                     'tool_uses_total': sum(r['tool_uses'] for r in runs),
                     'commits_total': sum(r['commits'] for r in runs), 'branches_total': sum(r['branches'] for r in runs),
                     'files_delivered_total': sum(r['files_delivered'] or 0 for r in runs),
                     'bytes_delivered_total': sum(r['bytes_delivered'] or 0 for r in runs),
                     'server_bytes_total': sum(r['server_bytes'] for r in runs),
                     'fragments_probed_total': sum(r['fragments_probed'] for r in runs),
                     'plaintext_hits_total': sum(r['plaintext_hits'] for r in runs),
                     'clones_identical': sum(1 for r in runs if r['clone_identical']),
                     'vaults_deleted': sum(1 for r in runs if r['deleted']),
                     'deletes_verified': sum(1 for r in runs if r['delete_verified']),
                     'roles': sorted({x for r in runs for x in r['roles']}),
                     'runs': runs},
        'talk': {'title': talk_j['title'], 'duration_s': talk_j['duration_s'], 'slides': len(beats), 'extras': len(extras),
                 'live_slides': len(live), 'live_on_player_clock': len(on_clock), 'live_with_steps': len(with_steps),
                 'other_slides': len(beats) - len(live)},
        'player': {'bytes': len(player.encode()), 'keys': keys, 'keys_case_folded': len(keys_folded), 'actions': actions,
                   'buttons': len(buttons), 'url_params': params, 'speeds': rates,
                   'gestures': ['tap = next step', 'swipe = next or previous slide'],
                   'clock_js_bytes': len(blob('site/assets/clock.js').encode()), 'sw_js_bytes': len(blob('site/sw.js').encode())},
        'site': {'at_commit': BASELINE, 'html_pages': len(pages), 'talk_slide_pages': sum(1 for p in pages if p.startswith('talk/slides/')),
                 'studio_pages': sum(1 for p in pages if p.startswith('studio/')),
                 'ruv_sgit_pages': sum(1 for p in pages if p.startswith('ruv-sgit/')),
                 'articles_src': art_src, 'articles_count': len(art_src)},
    }
    if mpath:
        msgs, images, excl = messages(mpath)
        before = [m for m in msgs if m['utc'] < talk]
        # a loop: a message from Dinis, then at least one commit before his next message (minute resolution)
        loops = 0
        for i, m in enumerate(before):
            end = before[i + 1]['utc'] if i + 1 < len(before) else talk
            if any(m['utc'] <= c['utc'] < end for c in commits): loops += 1
        out['feedback'] = {'rule': messages.__doc__.split('\n', 1)[1].strip(), 'messages_total': len(msgs), 'before_talk': len(before),
                           'after_talk': len(msgs) - len(before), 'with_screenshots': sum(1 for m in msgs if m['has_image']),
                           'screenshots': images, 'words': sum(m['words'] for m in msgs), 'excluded_sections': excl,
                           'first_utc': msgs[0]['utc'].isoformat(), 'last_before_talk_utc': before[-1]['utc'].isoformat(),
                           'loops_message_then_commit': loops}
    elif 'feedback' in prev:
        out['feedback'] = prev['feedback']
    OUT.write_text(json.dumps(out, indent=1, default=str) + '\n')
    print(json.dumps({k: v for k, v in out.items() if k != 'ruv_sgit'}, indent=1, default=str))
    print(json.dumps({k: v for k, v in out['ruv_sgit'].items() if k != 'runs'}, indent=1))


if __name__ == '__main__':
    main()
