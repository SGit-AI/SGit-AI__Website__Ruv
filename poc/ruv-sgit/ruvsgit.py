#!/usr/bin/env python3
"""ruv.sgit: a Ruflo hive (queen + workers in parallel) whose shared memory and output is one EPHEMERAL sgit vault per run.

  server-start            start a local SG/Send vault server (disk storage in ~/.ruv-sgit/store, a token made here)
  open    RUN SPEC        hive: init, one specialist per role, one task per deliverable; vault: init, brief committed
  deliver RUN WORKER ROLE SRC   a worker's output onto its own vault branch, pushed, merged into `current`
  close   RUN WORKERS.json      measure the vault (history, files, bytes, server store, plaintext probe, fresh clone)
                                and write the ledger: site/data/vaults.json + evidence/ruv-sgit/RUN.json
  delete  RUN             ephemeral, private (client work): the vault's objects are removed from the server store; never published
  seal    RUN [--keep-remote]   public examples only: publish the vault (READ key) to site/vaults/RUN/, clone it back from a
                                static host, delete it on the server, then DELETE THE VAULT KEY: the vault is immutable
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
LEDGER = pathlib.Path(os.environ.get('RUVSGIT_LEDGER', REPO / 'site/data/vaults.json'))      # scripts/offline.sh points these at out/offline/
EVIDENCE = pathlib.Path(os.environ.get('RUVSGIT_EVIDENCE', REPO / 'evidence/ruv-sgit'))
SITE = pathlib.Path(os.environ.get('RUVSGIT_SITE', REPO / 'site'))            # seal publishes into SITE/vaults/<run>/
PUBLIC_BASE = os.environ.get('RUVSGIT_PUBLIC_BASE', 'https://ruv.sgit.ai/')    # where SITE is served
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
             'files_delivered': sum(b['files'] for b in st['branches']), 'bytes_delivered': sum(b['bytes'] for b in st['branches']),   # the brief is in files/bytes_plain, not here
             'server_store': {'files': len(sf), 'bytes': sum(f.stat().st_size for f in sf), 'plaintext_hits': hits,
                              'probe': f'{len(probes)} text fragments from the delivered files, searched for in every byte the server stored'},
             'clone': {'ms': clone_ms, 'files': len(cf), 'identical': cf == plain},
             'ops': st['ops'], 'ruflo': st['ruflo'], 'history': history, 'workers': W}
    out = EVIDENCE; out.mkdir(parents=True, exist_ok=True)
    (out / f'{run}.json').write_text(json.dumps(entry, indent=1))
    ledger(entry); R.save()
    print(f"closed {run}: {entry['commits']} commits, {entry['files']} files, {entry['bytes_plain']} B plaintext; server holds {entry['server_store']['files']} files, plaintext hits {hits}; clone identical {entry['clone']['identical']} in {clone_ms} ms")

def ledger(entry):
    L = json.loads(LEDGER.read_text()) if LEDGER.exists() else {'vaults': []}
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    L['sample'] = False; L['updated'] = now()
    L['server'] = 'a local SG/Send vault server (sgraph-ai-app-send, disk storage), one process, on the machine that ran the hive'
    L['vaults'] = [v for v in L['vaults'] if v['run'] != entry['run']] + [{k: v for k, v in entry.items() if k != 'ruflo'}]
    LEDGER.write_text(json.dumps(L, indent=1))

def delete(run):
    R = Run(run); vid = R.state.get('vault_id')
    store = HOME / 'store'; gone = 0
    key = secret(f'runs/{run}/vault.key')
    for p in sorted(store.rglob('*'), key=lambda p: -len(p.parts)):
        if vid and vid in p.as_posix() and p.exists():
            if p.is_dir(): shutil.rmtree(p, ignore_errors=True)
            else: p.unlink()
            gone += 1
    # check the delete before the key is destroyed: nothing in the store is named by the vault id, and a clone with the key now fails
    left = sum(1 for p in store.rglob('*') if vid and vid in p.as_posix())
    tmp = pathlib.Path(tempfile.mkdtemp(prefix='ruvsgit-gone-'))
    r = R.sgit('clone-after-delete', ['clone', '--base-url', BASE, '--token', token(), '-', str(tmp / 'c')], cwd=tmp, stdin=key, check=False)
    shutil.rmtree(tmp, ignore_errors=True)
    check = {'store_paths_left': left, 'clone_after_delete': 'failed' if r.returncode else 'SUCCEEDED (not deleted)'}
    shutil.rmtree(R.vault, ignore_errors=True)
    (HOME / 'runs' / run / 'vault.key').unlink(missing_ok=True)
    R.state['deleted_at'] = now(); R.state['deleted_paths'] = gone; R.state['delete_check'] = check; R.save()
    ev = EVIDENCE / f'{run}.json'
    if ev.exists():
        e = json.loads(ev.read_text()); e['deleted_at'] = R.state['deleted_at']; e['deleted_paths'] = gone; e['delete_check'] = check; ev.write_text(json.dumps(e, indent=1)); ledger(e)
    print(f'{run}: vault {vid} deleted ({gone} store paths named by its id removed, {left} left; a clone with the key afterwards: {check["clone_after_delete"]}; key and working copy gone)')

def tree_hashes(root):
    return {f.relative_to(root).as_posix(): hashlib.sha256(f.read_bytes()).hexdigest() for f in root.rglob('*') if f.is_file() and '.sg_vault' not in f.parts}

def static_server(root):
    """a throwaway GET-only host for `root` on 127.0.0.1 (a free port), for the clone-back check"""
    import functools, http.server, threading
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(root)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv

def seal(run, keep_remote=False):
    """the end of a public run: publish the vault as a static folder with its READ key on the site, prove it clones back
    from a plain GET host, delete it from the vault server, then delete the vault key. No key: no writer, the vault is immutable.
    Only for runs that are public on purpose (examples); client runs end with `delete` and are never published."""
    R = Run(run); st = R.state; vid = st.get('vault_id')
    kf = HOME / 'runs' / run / 'vault.key'
    if not st.get('closed_at'): raise SystemExit(f'{run}: close the run before sealing it')
    if st.get('sealed_at') or not kf.exists(): raise SystemExit(f'{run}: already sealed or deleted (no vault key)')
    ev = EVIDENCE / f'{run}.json'
    if not ev.exists(): raise SystemExit(f'{run}: no evidence at {ev}; run close first')
    plain = tree_hashes(R.vault)
    # (b) the static surface: index.html loader, manifest.json, cover.json and the READ key file (--visibility public: irreversible)
    R.sgit('publish', ['publish', '--visibility', 'public', '--yes', '.'])
    pub = R.vault / '.sg_vault' / 'publish'
    # (a) the READ key: publish names a file after it (sgit_public_read_<64 hex>); kept in the run folder, 0600, like the vault key
    rk = [p.name for p in pub.iterdir() if re.fullmatch(r'sgit_public_read_[0-9a-f]{64}', p.name)]
    if len(rk) != 1: raise SystemExit(f'{run}: publish wrote {len(rk)} read-key files; expected 1')
    read_key = f'{rk[0]}:{vid}'; secret(f'runs/{run}/read.key', read_key)
    man = json.loads((pub / 'manifest.json').read_text())
    if man.get('vault_id') != vid or man.get('visibility') != 'public': raise SystemExit(f'{run}: manifest does not match the run')
    # (c) the deployable folder: the plaintext surface + the objects the manifest lists, at the api-path the manifest declares
    #     (vaults/<run>/api/vault/read/<vault id>/bare/…), the path `sgit vault serve` and the static SG/Vault transport read.
    #     Only manifest-listed bare/ objects are copied; .sg_vault/local (vault key, token, PEM) is never touched.
    dest = SITE / 'vaults' / run
    if dest.exists(): shutil.rmtree(dest)
    dest.mkdir(parents=True)
    for p in pub.iterdir():
        if p.is_file(): shutil.copy2(p, dest / p.name)
    obj_root = dest / 'api' / 'vault' / 'read' / vid; nbytes = 0
    for o in man['objects']:
        fid = o['file_id']
        if not fid.startswith('bare/') or '..' in fid: raise SystemExit(f'{run}: manifest lists an unexpected path {fid!r}')
        src = R.vault / '.sg_vault' / fid; data = src.read_bytes()
        if hashlib.sha256(data).hexdigest() != o['sha256']: raise SystemExit(f'{run}: {fid} does not match its manifest hash')
        out = obj_root / fid; out.parent.mkdir(parents=True, exist_ok=True); out.write_bytes(data); nbytes += len(data)
    # prove it: a fresh clone with only the READ key, from a plain GET host serving the site folder
    srv = static_server(SITE); url = f'http://127.0.0.1:{srv.server_address[1]}/vaults/{run}/'
    tmp = pathlib.Path(tempfile.mkdtemp(prefix='ruvsgit-sealed-'))
    try:
        t0 = time.time()
        c = R.sgit('clone-static', ['clone', '--base-url', url, '-', str(tmp / 'c')], cwd=tmp, stdin=read_key, check=False)
        clone_ms = round((time.time() - t0) * 1000)
        cf = tree_hashes(tmp / 'c') if c.returncode == 0 else {}
        (tmp / 'c' / 'write-probe.md').write_text('a write after the seal\n') if c.returncode == 0 else None
        w = R.sgit('commit-static', ['commit', '-m', 'write after seal'], cwd=tmp / 'c', check=False) if c.returncode == 0 else None
    finally:
        srv.shutdown(); shutil.rmtree(tmp, ignore_errors=True)
    if c.returncode or cf != plain: raise SystemExit(f'{run}: the published folder did not clone back identical; the vault key is kept')
    check = {'clone_static': {'ms': clone_ms, 'files': len(cf), 'identical': True},
             'write_with_read_key': 'refused' if w.returncode else 'ACCEPTED (not sealed)'}
    # (e) the published folder is now the artifact: hard-delete the vault on the server, checked with the key before it goes
    if not keep_remote:
        R.sgit('delete-on-remote', ['vault', 'delete-on-remote', '--yes', '--json', '--token', token(), '.'])
        tmp = pathlib.Path(tempfile.mkdtemp(prefix='ruvsgit-gone-'))
        r = R.sgit('clone-after-delete', ['clone', '--base-url', BASE, '--token', token(), '-', str(tmp / 'c')], cwd=tmp, stdin=secret(f'runs/{run}/vault.key'), check=False)
        shutil.rmtree(tmp, ignore_errors=True)
        check['server_clone_after_delete'] = 'failed' if r.returncode else 'SUCCEEDED (not deleted)'
    # (d) the seal: the vault key is destroyed (its file, and the working copy whose .sg_vault/local holds it and the token)
    kf.unlink(); shutil.rmtree(R.vault, ignore_errors=True)
    check['vault_key_left'] = kf.exists() or R.vault.exists()
    st['sealed_at'] = now()
    published = {'path': f'vaults/{run}/', 'read_key': read_key, 'vault_id': vid, 'sealed_at': st['sealed_at'],
                 'files': sum(1 for p in dest.rglob('*') if p.is_file()), 'objects': len(man['objects']), 'bytes_objects': nbytes,
                 'viewer_url': f"{PUBLIC_BASE}vaults/{run}/#{rk[0]}%3A{vid}",
                 'clone': f'sgit clone {read_key} --base-url {PUBLIC_BASE}vaults/{run}/'}
    st['published'] = published; st['seal_check'] = check; R.save()
    e = json.loads(ev.read_text()); e.update(sealed_at=st['sealed_at'], published=published, seal_check=check)
    ev.write_text(json.dumps(e, indent=1)); ledger(e)
    print(f"{run}: sealed. vault {vid} published at site/vaults/{run}/ ({len(man['objects'])} objects, {nbytes} B); "
          f"static clone identical ({len(cf)} files, {clone_ms} ms); a write with the read key: {check['write_with_read_key']}; "
          f"server copy: {check.get('server_clone_after_delete', 'kept')}; vault key destroyed")

if __name__ == '__main__':
    a = sys.argv[1:]
    {'server-start': lambda: server_start(), 'server-stop': lambda: server_stop(), 'open': lambda: open_run(a[1], a[2]),
     'deliver': lambda: deliver(a[1], a[2], a[3], a[4]), 'close': lambda: close(a[1], a[2]), 'delete': lambda: delete(a[1]),
     'seal': lambda: seal(a[1], keep_remote='--keep-remote' in a)}[a[0]]()
