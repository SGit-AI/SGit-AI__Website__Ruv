#!/usr/bin/env python3
"""The worked examples on rules/index.html add up, to the penny (r15-rules acceptance check, article No. 9).

Reads the JSON block <script id="worked-examples"> in site/rules/index.html and checks, for every priced case:
  - the shares plus the direct costs equal the price, in whole pence;
  - the shares are equal to within one penny (rule 6: split equally);
  - the price is the list price of its offer in site/data/offers.json (rule 11: public fixed list prices);
  - the visible table row for the case shows the same price and every share (so the prose and the data agree).
Exit 1 on any mismatch. Usage: python3 site/build/rules_check.py"""
import html as H, json, pathlib, re, sys

SITE = pathlib.Path(__file__).resolve().parents[1]
page = (SITE / 'rules' / 'index.html').read_text(encoding='utf-8')
offers = json.loads((SITE / 'data' / 'offers.json').read_text(encoding='utf-8'))
list_price = {i['id']: i['price'] for g in offers['groups'] for i in g['items']}

m = re.search(r'<script type="application/json" id="worked-examples">(.*?)</script>', page, re.S)
if not m: sys.exit('FAIL rules/index.html: no <script id="worked-examples"> block')
data = json.loads(m.group(1))

def pence(x): return int(round(float(x) * 100))
def money(p): return f'£{p // 100:,}' + (f'.{p % 100:02d}' if p % 100 else '')
def row(case_id):
    r = re.search(r'<tr data-case="' + re.escape(case_id) + r'">(.*?)</tr>', page, re.S)
    return H.unescape(re.sub(r'<[^>]+>', ' ', r.group(1))) if r else None

fails, checked = [], 0
for c in data['cases']:
    cid = c['id']; text = row(cid)
    if text is None: fails.append(f'{cid}: no table row'); continue
    if 'price' not in c:   # the custom (rule 8) and do-it-yourself (rule 2) cases have no figures
        if '£' in text: fails.append(f'{cid}: the row shows a figure but the data has no price')
        print(f'  {cid}: no figures ({c.get("custom") or c.get("nothing")})'); continue
    price, costs, shares = pence(c['price']), pence(c.get('direct_costs', 0)), [pence(s) for s in c['shares']]
    total = sum(shares) + costs
    ok = total == price
    if not ok: fails.append(f'{cid}: shares {money(sum(shares))} + costs {money(costs)} = {money(total)}, not the price {money(price)}')
    if max(shares) - min(shares) > 1: fails.append(f'{cid}: shares differ by more than a penny ({[money(s) for s in shares]})')
    lp = list_price.get(c['offer'])
    if lp is None: fails.append(f'{cid}: offer {c["offer"]} is not in data/offers.json')
    elif pence(lp) != price: fails.append(f'{cid}: price {money(price)} is not the list price of {c["offer"]} ({money(pence(lp))})')
    for p in [price] + sorted(set(shares)):
        if money(p) not in text: fails.append(f'{cid}: the table row does not show {money(p)}')
    checked += 1
    print(f'  {cid}: {money(price)} ({c["offer"]}) = ' + ' + '.join(money(s) for s in shares) + (f' + costs {money(costs)}' if costs else '') + (' ok' if ok else ' MISMATCH'))

print(f'{checked} priced worked examples checked against data/offers.json')
for f in fails: print('FAIL', f)
sys.exit(1 if fails else 0)
