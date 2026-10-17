#!/usr/bin/env python3
"""ruv.sgit: a Ruflo hive (queen + workers in parallel) whose shared memory and output is one EPHEMERAL sgit vault per run.

  server-start            start a local SG/Send vault server (disk storage in ~/.ruv-sgit/store, a token made here)
  open    RUN SPEC        hive: init, one specialist per role, one task per deliverable; vault: init, brief committed
  deliver RUN WORKER ROLE SRC   a worker's output onto its own vault branch, pushed, merged into `current`
  close   RUN WORKERS.json      measure the vault (history, files, bytes, server store, plaintext probe, fresh clone)
                                and write the ledger: site/data/vaults.json + evidence/ruv-sgit/RUN.json
  delete  RUN             ephemeral, private (client work): the vault's objects are removed from the server store; never published
  seal    RUN [--keep-remote] [--no-ui-check]   public examples only: push the vault (all branches, full history) to the
                                SG/Send publish server (dev.send.sgraph.ai), take its READ key, check a fresh read-only clone
                                from there (identical, writes refused) and the vault UI (dev.vault.sgraph.ai), delete the
                                local-server copy, then DELETE THE VAULT KEY: the vault is immutable. Only the reference
                                (server, vault id, read key, viewer URL, clone command) goes into the ledger
  server-stop

Every sgit and ruflo call is timed into the run's trace. The vault key, the server token and the publish token live only in
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
PUBLISH_SERVER = os.environ.get('RUVSGIT_PUBLISH_SERVER', 'https://dev.send.sgraph.ai')     # seal pushes public example vaults here
PUBLISH_REMOTE = 'sgraph'
VIEWER_BASE = os.environ.get('RUVSGIT_VIEWER_BASE', 'https://dev.vault.sgraph.ai/en-gb/')      # the official SG/Vault UI for that server
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
    L['published_on'] = {'server': PUBLISH_SERVER, 'viewer': VIEWER_BASE,
                         'note': 'sealed example runs only: the vault lives on this SG/Send server and opens in its vault UI with the published read key; the repository holds only the reference'}
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

def bare_hashes(root):
    """the encrypted store of a working copy, as the server holds it: every object, branch ref, index and key file"""
    b = root / '.sg_vault' / 'bare'
    return {f.relative_to(b).as_posix(): hashlib.sha256(f.read_bytes()).hexdigest()
            for d in ('data', 'refs', 'indexes', 'keys') if (b / d).exists() for f in (b / d).rglob('*') if f.is_file()}

def publish_token():
    """the SG/Send access token for the publish server: env RUVSGIT_PUBLISH_TOKEN, else RUVSGIT_HOME/publish.token (0600); never printed"""
    t = os.environ.get('RUVSGIT_PUBLISH_TOKEN') or (secret('publish.token') if (HOME / 'publish.token').exists() else '')
    if not t: raise SystemExit(f'no publish token: put the SG/Send access token in {HOME}/publish.token (mode 0600) or RUVSGIT_PUBLISH_TOKEN')
    return t

def ui_check(run, viewer_url, names, shot):
    """open the viewer URL in the official SG/Vault UI (headless Chromium, playwright-core) and screenshot it;
    passes when every top-level name of the vault is shown"""
    script = pathlib.Path(__file__).with_name('vault-ui-check.mjs')
    r = subprocess.run(['node', str(script), viewer_url, str(shot), *names], capture_output=True, text=True, timeout=180)
    try: out = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception: raise SystemExit(f'{run}: the vault UI check did not run: ' + scrub(r.stderr)[-400:])
    return out

def seal(run, keep_remote=False, ui=True):
    """the end of a public run: push the vault (every branch, its whole history) to the SG/Send publish server, take its READ key,
    prove a fresh read-only clone from that server is identical and cannot write, open it in the official vault UI, delete the
    local-server copy, then DELETE THE VAULT KEY. No key: no writer, the vault is immutable. The repository keeps only the
    reference (server, vault id, read key, viewer URL, clone command), never the vault's files.
    Only for runs that are public on purpose (examples); client runs end with `delete` and are never published."""
    R = Run(run); st = R.state; vid = st.get('vault_id')
    kf = HOME / 'runs' / run / 'vault.key'
    if not st.get('closed_at'): raise SystemExit(f'{run}: close the run before sealing it')
    if st.get('sealed_at') or not kf.exists(): raise SystemExit(f'{run}: already sealed or deleted (no vault key)')
    ev = EVIDENCE / f'{run}.json'
    if not ev.exists(): raise SystemExit(f'{run}: no evidence at {ev}; run close first')
    ptok = publish_token()
    plain = tree_hashes(R.vault)
    nbytes = sum(f.stat().st_size for f in R.vault.rglob('*') if f.is_file() and '.sg_vault' not in f.parts)
    # (a) the vault onto the publish server: a named remote, then push. A first push to a remote re-syncs the whole bare
    #     store (every commit, every named branch ref, the branch index), checked below against a fresh clone's store.
    R.sgit('remote-add', ['remote', 'add', '--default', PUBLISH_REMOTE, PUBLISH_SERVER], check=False)
    if PUBLISH_SERVER not in R.sgit('remote-list', ['remote', 'list']).stdout: raise SystemExit(f'{run}: remote {PUBLISH_REMOTE} not configured')
    t0 = time.time(); R.sgit('push-publish', ['push', '--remote', PUBLISH_REMOTE, '--token', ptok]); push_ms = round((time.time() - t0) * 1000)
    # (b) the READ key: `sgit publish --visibility public` names a file after it (sgit_public_read_<64 hex>) in .sg_vault/publish/
    #     (local only; nothing is uploaded by it). Kept in the run folder, 0600, like the vault key.
    R.sgit('publish', ['publish', '--visibility', 'public', '--yes', '.'])
    pub = R.vault / '.sg_vault' / 'publish'
    rk = [p.name for p in pub.iterdir() if re.fullmatch(r'sgit_public_read_[0-9a-f]{64}', p.name)]
    if len(rk) != 1: raise SystemExit(f'{run}: publish wrote {len(rk)} read-key files; expected 1')
    read_key = f'{rk[0]}:{vid}'; secret(f'runs/{run}/read.key', read_key)
    man = json.loads((pub / 'manifest.json').read_text())
    if man.get('vault_id') != vid or man.get('visibility') != 'public': raise SystemExit(f'{run}: manifest does not match the run')
    # (c) prove it: a fresh clone from the publish server with only the READ key: same files, same encrypted store
    #     (all branches, full history), and a write from it is refused
    tmp = pathlib.Path(tempfile.mkdtemp(prefix='ruvsgit-sealed-'))
    try:
        t0 = time.time()
        c = R.sgit('clone-published', ['clone', '--base-url', PUBLISH_SERVER, '-', str(tmp / 'c')], cwd=tmp, stdin=read_key, check=False)
        clone_ms = round((time.time() - t0) * 1000)
        cf = tree_hashes(tmp / 'c') if c.returncode == 0 else {}
        cb = bare_hashes(tmp / 'c') if c.returncode == 0 else {}
        if c.returncode == 0:
            (tmp / 'c' / 'write-probe.md').write_text('a write after the seal\n')
            w = R.sgit('commit-published', ['commit', '-m', 'write after seal'], cwd=tmp / 'c', check=False)
            p = R.sgit('push-published', ['push', '--token', ptok], cwd=tmp / 'c', check=False)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    vb = bare_hashes(R.vault)
    if c.returncode or cf != plain: raise SystemExit(f'{run}: the published vault did not clone back identical; the vault key is kept')
    if cb != vb: raise SystemExit(f'{run}: the server store differs from the run\'s ({len(cb)} vs {len(vb)} objects); the vault key is kept')
    if not (w.returncode and p.returncode): raise SystemExit(f'{run}: a write with the read key was not refused; the vault key is kept')
    refs = sum(1 for k in vb if k.startswith('refs/ref-pid-muw-'))
    check = {'server': PUBLISH_SERVER, 'push_ms': push_ms,
             'clone_published': {'ms': clone_ms, 'files': len(cf), 'identical': True, 'store_objects': len(cb), 'store_identical': True, 'named_branch_refs': refs},
             'write_with_read_key': 'refused (commit and push)'}
    viewer = f'{VIEWER_BASE}#{read_key}'
    # (c) the official vault UI opens it (headless Chromium), screenshot kept as evidence
    if ui:
        shot = EVIDENCE / f'{run}-vault-ui.png'
        u = ui_check(run, viewer, sorted({k.split('/')[0] for k in plain}), shot)
        if not u.get('ok'): raise SystemExit(f'{run}: the vault UI did not show the vault ({u.get("missing")}, {u.get("errors")}); the vault key is kept')
        check['vault_ui'] = {'opened': True, 'shows': u['found'], 'title': u.get('title'), 'screenshot': shot.resolve().relative_to(REPO).as_posix() if shot.resolve().is_relative_to(REPO) else str(shot)}
    # (d) the local-server copy is deleted (--base-url pins it: the default remote is now the publish server), checked with the key
    if not keep_remote:
        R.sgit('delete-local', ['vault', 'delete-on-remote', '--base-url', BASE, '--yes', '--json', '--token', token(), '.'])
        tmp = pathlib.Path(tempfile.mkdtemp(prefix='ruvsgit-gone-'))
        r = R.sgit('clone-after-delete', ['clone', '--base-url', BASE, '--token', token(), '-', str(tmp / 'c')], cwd=tmp, stdin=secret(f'runs/{run}/vault.key'), check=False)
        shutil.rmtree(tmp, ignore_errors=True)
        check['local_server_clone_after_delete'] = 'failed' if r.returncode else 'SUCCEEDED (not deleted)'
    # (e) the seal: the vault key is destroyed (its file, and the working copy whose .sg_vault/local holds it and the tokens)
    kf.unlink(); shutil.rmtree(R.vault, ignore_errors=True)
    check['vault_key_left'] = kf.exists() or R.vault.exists()
    st['sealed_at'] = now()
    # (f) only the reference is recorded: no vault file is written into the repository
    published = {'server': PUBLISH_SERVER, 'vault_id': vid, 'read_key': read_key, 'viewer_url': viewer,
                 'clone': f'sgit clone {read_key}', 'sealed_at': st['sealed_at'],
                 'files': len(plain), 'bytes': nbytes}
    st['published'] = published; st['seal_check'] = check; R.save()
    e = json.loads(ev.read_text()); e.update(sealed_at=st['sealed_at'], published=published, seal_check=check, ops=st['ops'])
    ev.write_text(json.dumps(e, indent=1)); ledger(e)
    print(f"{run}: sealed. vault {vid} on {PUBLISH_SERVER}; fresh read-only clone identical ({len(cf)} files, {len(cb)} store objects, "
          f"{refs} named branches, {clone_ms} ms); a write with the read key: refused; vault UI: {'opened' if ui else 'not checked'}; "
          f"local server copy: {check.get('local_server_clone_after_delete', 'kept')}; vault key destroyed")

if __name__ == '__main__':
    a = sys.argv[1:]
    {'server-start': lambda: server_start(), 'server-stop': lambda: server_stop(), 'open': lambda: open_run(a[1], a[2]),
     'deliver': lambda: deliver(a[1], a[2], a[3], a[4]), 'close': lambda: close(a[1], a[2]), 'delete': lambda: delete(a[1]),
     'seal': lambda: seal(a[1], keep_remote='--keep-remote' in a, ui='--no-ui-check' not in a)}[a[0]]()
