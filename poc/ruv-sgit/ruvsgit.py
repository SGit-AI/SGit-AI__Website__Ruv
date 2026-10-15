#!/usr/bin/env python3
"""ruv.sgit: a Ruflo hive (queen + workers in parallel) whose shared memory and output is one EPHEMERAL sgit vault per run.

  server-start            start a local SG/Send vault server (disk storage in ~/.ruv-sgit/store, a token made here)
  open    RUN SPEC        hive: init, one specialist per role, one task per deliverable; vault: init, brief committed
  deliver RUN WORKER ROLE SRC   a worker's output onto its own vault branch, pushed, merged into `current`
  close   RUN WORKERS.json      measure the vault (history, files, bytes, server store, plaintext probe, fresh clone)
                                and write the ledger: site/data/vaults.json + evidence/ruv-sgit/RUN.json
  delete  RUN             ephemeral: the vault's objects are removed from the server store; the ledger records when
  server-stop

Every sgit and ruflo call is timed into the run's trace. The vault key and the server token live only in
~/.ruv-sgit (mode 0600), are passed on stdin or in files, and are never printed, logged or committed.
Usage: python3 poc/ruv-sgit/ruvsgit.py <command> ...   (from the repo root; npm ci and pip install sgit-ai first)"""
import hashlib, json, os, pathlib, re, secrets, shutil, signal, subprocess, sys, tempfile, time, urllib.request
from datetime import datetime, timezone

REPO = pathlib.Path(__file__).resolve().parents[2]
HOME = pathlib.Path(os.environ.get('RUVSGIT_HOME', pathlib.Path.home() / '.ruv-sgit'))
PORT = int(os.environ.get('RUVSGIT_PORT', '8080'))
BASE = f'http://127.0.0.1:{PORT}'
RUFLO = str(REPO / 'node_modules/.bin/ruflo')
SGIT = os.environ.get('RUVSGIT_SGIT', 'sgit')
LEDGER = REPO / 'site/data/vaults.json'
now = lambda: datetime.now(timezone.utc).isoformat(timespec='seconds')

def secret(name, value=None):
    """read or write a secret file under ~/.ruv-sgit, mode 0600"""
    p = HOME / name
    if value is not None:
        p.parent.mkdir(parents=True, exist_ok=True); p.write_text(value); p.chmod(0o600)
    return p.read_text().strip()

class Run:
    def __init__(self, run):
        self.run, self.dir = run, HOME / 'runs' / run
        self.state_f = self.dir / 'state.json'
        self.state = json.loads(self.state_f.read_text()) if self.state_f.exists() else {'run': run, 'ops': [], 'ruflo': [], 'branches': []}
    def save(self): self.dir.mkdir(parents=True, exist_ok=True); self.state_f.write_text(json.dumps(self.state, indent=1))
    @property
    def vault(self): return self.dir / 'vault'

    def sgit(self, op, args, cwd=None, stdin=None, check=True):
        t0 = time.time()
        r = subprocess.run([SGIT, *args], cwd=cwd or self.vault, input=stdin, capture_output=True, text=True)
        ms = round((time.time() - t0) * 1000)
        self.state['ops'].append({'op': op, 'ms': ms, 'rc': r.returncode})
        if check and r.returncode:
            raise SystemExit(f'sgit {op} failed (rc {r.returncode}): ' + scrub(r.stderr or r.stdout)[-400:])
        return r

    def ruflo(self, actor, args):
        work = pathlib.Path(self.state['hive_dir'])
        t0 = time.time(); r = subprocess.run([RUFLO, *args], cwd=work, capture_output=True, text=True)
        rec = {'seq': len(self.state['ruflo']) + 1, 'actor': actor, 'cmd': ' '.join(args), 'rc': r.returncode, 'ms': round((time.time() - t0) * 1000)}
        self.state['ruflo'].append(rec); return r

def scrub(s):   # never let a key or token reach a message
    s = re.sub(r'[A-Za-z0-9_-]{40,}', '‹redacted›', s)
    return s

def token(): return secret('server.token')

def server_start():
    HOME.mkdir(parents=True, exist_ok=True)
    tok = secret('server.token', secrets.token_hex(32)) if not (HOME / 'server.token').exists() else token()
    store = HOME / 'store'; store.mkdir(exist_ok=True)
    env = {**os.environ, 'SEND__STORAGE_MODE': 'disk', 'SEND__DISK_PATH': str(store), 'SGRAPH_SEND__ACCESS_TOKEN': tok, 'PORT': str(PORT)}
    py = os.environ.get('RUVSGIT_SERVER_PY', sys.executable)
    log = open(HOME / 'server.log', 'a')
    p = subprocess.Popen([py, '-m', 'sgraph_ai_app_send__docker.serve'], env=env, stdout=log, stderr=log, start_new_session=True)
    (HOME / 'server.pid').write_text(str(p.pid))
    for _ in range(60):
        try:
            req = urllib.request.Request(f'{BASE}/api/info/health', headers={'x-sgraph-access-token': tok})
            if json.loads(urllib.request.urlopen(req, timeout=2).read()).get('status') == 'ok': print('vault server up at', BASE); return
        except Exception: time.sleep(1)
    raise SystemExit('vault server did not answer; see ~/.ruv-sgit/server.log')

def server_stop():
    pid = HOME / 'server.pid'
    if pid.exists():
        try: os.killpg(int(pid.read_text()), signal.SIGTERM)
        except ProcessLookupError: pass
        pid.unlink(); print('vault server stopped')

def open_run(run, spec_path):
    R = Run(run); spec = json.loads(pathlib.Path(spec_path).read_text())
    R.state.update(purpose=spec['purpose'], feedback=spec.get('feedback', ''), created_at=now(), roles=[w['role'] for w in spec['workers']])
    # the hive: a fresh folder per run (Ruflo anchors each project's policy ledger outside it; a reused path is refused)
    hive = R.dir / f'hive-{int(time.time())}'; hive.mkdir(parents=True); R.state['hive_dir'] = str(hive)
    R.ruflo('queen', ['hive-mind', 'init', '-t', 'hierarchical-mesh', '-c', 'byzantine', '-m', '12'])
    for w in spec['workers']:
        R.ruflo('queen', ['hive-mind', 'spawn', '-n', '1', '-t', w['role'], '-r', 'specialist', '-p', w['id']])
    for w in spec['workers']:
        R.ruflo('conductor', ['hive-mind', 'task', '-d', f"{w['id']}: {w['task']}", '-p', 'high'])
    R.ruflo('conductor', ['hive-mind', 'broadcast', '-m', f"run {run}: {spec['purpose']}", '-f', 'conductor'])
    # the vault: created on the local server; the key goes to a 0600 file, never to the screen
    R.vault.mkdir(parents=True, exist_ok=True)
    (R.vault / 'brief').mkdir(exist_ok=True)
    shutil.copy(spec_path, R.vault / 'brief' / 'spec.json')
    (R.vault / 'brief' / 'feedback.md').write_text(f"# Feedback that started run {run}\n\n{spec.get('feedback', '')}\n")
    r = R.sgit('init', ['init', '--existing', '--base-url', BASE, '--token', token(), '.'], stdin='')   # --existing: the brief is already in the folder
    key = re.search(r'Vault key:\s*(\S+)', r.stdout); vid = re.search(r'Vault ID:\s*(\S+)', r.stdout)
    if not key: raise SystemExit('sgit init printed no vault key; output shape changed (not shown: it may hold the key)')
    secret(f'runs/{run}/vault.key', key.group(1)); R.state['vault_id'] = vid.group(1) if vid else None
    R.sgit('commit', ['commit', '-m', f'brief: run {run}'])
    R.sgit('push', ['push', '--token', token()])
    R.save(); print(f"run {run} open: vault {R.state['vault_id']}, {len(spec['workers'])} workers, hive in {hive.name}")

def deliver(run, worker, role, src):
    R = Run(run); src = pathlib.Path(src)
    br = f'w-{worker}'; t0 = time.time()
    R.sgit('branch-new', ['branch', 'new', br])
    dest = R.vault / 'workers' / worker
    if dest.exists(): shutil.rmtree(dest)
    shutil.copytree(src, dest)
    files = [f for f in dest.rglob('*') if f.is_file()]
    R.sgit('commit', ['commit', '-m', f'{role} {worker}: delivered {len(files)} files'])
    R.sgit('push', ['push', '--token', token()])
    write_ms = round((time.time() - t0) * 1000); t1 = time.time()
    R.sgit('branch-switch', ['branch', 'switch', 'current'])
    R.sgit('merge', ['branch', 'merge', br])
    R.sgit('push', ['push', '--token', token()])
    merge_ms = round((time.time() - t1) * 1000)
    digest = hashlib.sha256(b''.join(f.read_bytes() for f in sorted(files))).hexdigest()[:16]
    R.ruflo(role, ['hive-mind', 'broadcast', '-m', f'delivered {worker} sha256:{digest} files:{len(files)}', '-f', role])
    R.state['branches'] = [b for b in R.state['branches'] if b['name'] != br] + [{'name': br, 'role': role, 'commits': 1, 'files': len(files), 'bytes': sum(f.stat().st_size for f in files), 'write_ms': write_ms, 'merge_ms': merge_ms}]
    R.save(); print(f'{worker}: {len(files)} files on {br}, merged into current ({write_ms} + {merge_ms} ms)')

def close(run, workers_json):
    R = Run(run)
    hist = R.sgit('history', ['history', 'log', '--json', '-n', '200'])
    try: H = json.loads(hist.stdout)
    except json.JSONDecodeError: H = []
    H = H.get('commits', H) if isinstance(H, dict) else H
    history = [{'id': str(c.get('commit_id') or c.get('id') or '').replace('obj-cas-imm-', '')[:12], 'message': c.get('message', ''), 'time': c.get('timestamp_iso'), 'files_added': len(c.get('files_added', [])), 'parents': len(c.get('parent_ids', []))} for c in H]
    files = [f for f in R.vault.rglob('*') if f.is_file() and '.sg_vault' not in f.parts]
    plain = {f.relative_to(R.vault).as_posix(): hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    # what the server holds: count and size the store, then look for plaintext from the delivered files in it
    store = HOME / 'store'; sf = [f for f in store.rglob('*') if f.is_file()]
    probes = []
    for f in files:
        txt = f.read_bytes()
        for m in re.finditer(rb'[A-Za-z][A-Za-z ,.]{24,}', txt):
            probes.append(m.group(0)[:32]);
            if len(probes) >= 40: break
        if len(probes) >= 40: break
    blob = b''.join(f.read_bytes() for f in sf)
    hits = sum(1 for p in probes if p in blob)
    # a fresh clone elsewhere gets back exactly what the workers delivered
    tmp = pathlib.Path(tempfile.mkdtemp(prefix='ruvsgit-clone-')); t0 = time.time()
    R.sgit('clone', ['clone', '--base-url', BASE, '--token', token(), '-', str(tmp / 'c')], cwd=tmp, stdin=secret(f'runs/{run}/vault.key'))
    clone_ms = round((time.time() - t0) * 1000)
    cf = {f.relative_to(tmp / 'c').as_posix(): hashlib.sha256(f.read_bytes()).hexdigest() for f in (tmp / 'c').rglob('*') if f.is_file() and '.sg_vault' not in f.parts}
    shutil.rmtree(tmp)
    R.ruflo('queen', ['hive-mind', 'status']); R.ruflo('queen', ['daemon', 'stop'])
    W = json.loads(pathlib.Path(workers_json).read_text())
    st = R.state; st['closed_at'] = now()
    entry = {'run': run, 'purpose': st['purpose'], 'feedback': st['feedback'], 'vault_id': st['vault_id'],
             'created_at': st['created_at'], 'closed_at': st['closed_at'], 'deleted_at': st.get('deleted_at'),
             'hive': {'workers': sum(1 for x in st['ruflo'] if 'hive-mind spawn' in x['cmd'] and x['rc'] == 0),
                      'tasks': sum(1 for x in st['ruflo'] if 'hive-mind task' in x['cmd'] and x['rc'] == 0),
                      'ruflo_calls': len(st['ruflo']), 'ruflo_ms': sum(x['ms'] for x in st['ruflo'])},
             'branches': st['branches'], 'commits': len(history), 'files': len(plain), 'bytes_plain': sum(f.stat().st_size for f in files),
             'server_store': {'files': len(sf), 'bytes': sum(f.stat().st_size for f in sf), 'plaintext_hits': hits,
                              'probe': f'{len(probes)} text fragments from the delivered files, searched for in every byte the server stored'},
             'clone': {'ms': clone_ms, 'files': len(cf), 'identical': cf == plain},
             'ops': st['ops'], 'ruflo': st['ruflo'], 'history': history, 'workers': W}
    out = REPO / 'evidence/ruv-sgit'; out.mkdir(parents=True, exist_ok=True)
    (out / f'{run}.json').write_text(json.dumps(entry, indent=1))
    ledger(entry); R.save()
    print(f"closed {run}: {entry['commits']} commits, {entry['files']} files, {entry['bytes_plain']} B plaintext; server holds {entry['server_store']['files']} files, plaintext hits {hits}; clone identical {entry['clone']['identical']} in {clone_ms} ms")

def ledger(entry):
    L = json.loads(LEDGER.read_text()) if LEDGER.exists() else {'vaults': []}
    L['sample'] = False; L['updated'] = now()
    L['server'] = 'a local SG/Send vault server (sgraph-ai-app-send, disk storage), one process, on the machine that ran the hive'
    L['vaults'] = [v for v in L['vaults'] if v['run'] != entry['run']] + [{k: v for k, v in entry.items() if k != 'ruflo'}]
    LEDGER.write_text(json.dumps(L, indent=1))

def delete(run):
    R = Run(run); vid = R.state.get('vault_id')
    store = HOME / 'store'; gone = 0
    for p in sorted(store.rglob('*'), key=lambda p: -len(p.parts)):
        if vid and vid in p.as_posix() and p.exists():
            if p.is_dir(): shutil.rmtree(p, ignore_errors=True)
            else: p.unlink()
            gone += 1
    shutil.rmtree(R.vault, ignore_errors=True)
    (HOME / 'runs' / run / 'vault.key').unlink(missing_ok=True)
    R.state['deleted_at'] = now(); R.state['deleted_paths'] = gone; R.save()
    ev = REPO / f'evidence/ruv-sgit/{run}.json'
    if ev.exists():
        e = json.loads(ev.read_text()); e['deleted_at'] = R.state['deleted_at']; e['deleted_paths'] = gone; ev.write_text(json.dumps(e, indent=1)); ledger(e)
    print(f'{run}: vault {vid} deleted ({gone} store paths named by its id removed; key and working copy gone)')

if __name__ == '__main__':
    a = sys.argv[1:]
    {'server-start': lambda: server_start(), 'server-stop': lambda: server_stop(), 'open': lambda: open_run(a[1], a[2]),
     'deliver': lambda: deliver(a[1], a[2], a[3], a[4]), 'close': lambda: close(a[1], a[2]), 'delete': lambda: delete(a[1])}[a[0]]()
