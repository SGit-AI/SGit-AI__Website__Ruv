"""Unit economics behind site/data/offers.json (r5-market, economist).
Edit the INPUTS block and re-run:  python3 model.py
Every price in offers.json is checked here against cost; nothing else is read."""

# ---------------- INPUTS (edit these) ----------------
FX_USD_PER_GBP = 1.30                      # assumption, editable
PRICES = {                                  # USD per million tokens, Anthropic first-party, cached 6 Oct 2026
    "fable-5.1":  {"in": 10.00, "out": 50.00, "cache_read": 0.25},
    "opus-5.5":   {"in": 4.00,  "out": 20.00, "cache_read": 0.20},
    "sonnet-5.5": {"in": 2.00,  "out": 10.00, "cache_read": 0.20},
    "haiku-5.5":  {"in": 0.10,  "out": 0.50,  "cache_read": None},   # prompts up to 100K; cache price not listed
}
HAIKU_CACHE_READ_ASSUMED = 0.01             # assumption: 10% of input, as for the others' order of magnitude
MIX = {"base": (0.75, 0.20, 0.05),          # (cache reads, fresh input incl. cache writes, output) share of tokens
       "conservative": (0.50, 0.40, 0.10),
       "worst": (0.00, 0.90, 0.10)}
HOST_OVERHEAD = 0.25                        # queen/host session tokens on top of workers' (not measured)
HUMAN_GBP_PER_HOUR = 75.0                   # loaded cost of the person on our side (assumption)
EC2_USD_PER_HOUR = {"small": 0.0472, "medium": 0.2331, "gpu": 1.277}   # eu-west-2 on-demand, aggregators
RUNNER = "medium"; RUNS_PER_RUNNER = 4      # shared runner: one m7i.xlarge, 4 runs at once (assumption)
STORAGE_GBP_PER_RUN = 0.05                  # sgit server + zip delivery allowance (assumption)
MARGIN_TARGET = 0.40; MARGIN_FLOOR = 0.35; STRESS_FLOOR = 0.15

# tiers: price GBP, Sonnet-equivalent M tokens, workers, wall-clock cap min, MB, operator minutes, BYOK delta
RUNS = {
    "run-s": dict(price=10, mtok=1,  workers=5,  cap_min=15, mb=50,  human_min=4,  byok=-1),
    "run-m": dict(price=20, mtok=3,  workers=10, cap_min=25, mb=100, human_min=6,  byok=-3),
    "run-l": dict(price=50, mtok=10, workers=20, cap_min=45, mb=100, human_min=12, byok=-10),
}
COMPUTE_BLOCK_H = 8; COMPUTE_FEE = 20.0; COMPUTE_EC2_MULT = 2.0
COMPUTE_HUMAN_MIN = 10; COMPUTE_EBS_GBP = 0.25   # start, check, stop; disk allowance (assumption)
REPO = {"repo-individual": (149, 1.0, 10), "repo-team": (499, 3.5, 25), "repo-white-label": (1500, 10.0, 50)}  # price, our hours/month, tooling GBP/month
EXPERT = {"expert-hours": (500, 2, 1), "expert-day": (1500, 7.5, 2), "expert-days": (5000, 30, 6)}  # price, hours delivered, prep/admin hours

# ---------------- MODEL ----------------
def cache(m):
    c = PRICES[m]["cache_read"]; return HAIKU_CACHE_READ_ASSUMED if c is None else c
def blended(m, mix="base"):
    cr, fi, out = MIX[mix]; p = PRICES[m]; return cr * cache(m) + fi * p["in"] + out * p["out"]
def run_cost(t, mix="base", fx=FX_USD_PER_GBP, host=HOST_OVERHEAD, rate=HUMAN_GBP_PER_HOUR, byok=False):
    tokens = 0 if byok else t["mtok"] * blended("sonnet-5.5", mix) * (1 + host) / fx
    human = t["human_min"] / 60 * rate
    infra = t["cap_min"] / 60 * EC2_USD_PER_HOUR[RUNNER] / RUNS_PER_RUNNER / fx + STORAGE_GBP_PER_RUN
    return tokens, human, infra
m = lambda p, c: (p - c) / p

if __name__ == "__main__":
    print("Blended USD/M by mix:")
    for k in MIX: print(f"  {k:12s}", {n: round(blended(n, k), 4) for n in PRICES})
    print("\nModel conversion of 1M Sonnet-equivalent (base mix):")
    for n in PRICES: print(f"  {n:10s} {blended('sonnet-5.5') / blended(n):.2f} M")
    print("\nRuns:")
    for k, t in RUNS.items():
        tok, hum, inf = run_cost(t); c = tok + hum + inf
        _, _, _ = run_cost(t, byok=True); cb = sum(run_cost(t, byok=True)); pb = t["price"] + t["byok"]
        print(f"  {k} £{t['price']}: tokens £{tok:.2f} + human £{hum:.2f} + infra £{inf:.3f} = £{c:.2f}  margin {m(t['price'], c):.0%} | BYOK £{pb}: cost £{cb:.2f} margin {m(pb, cb):.0%}")
        for name, kw in [("conservative mix", dict(mix="conservative")), ("worst mix", dict(mix="worst")),
                         ("FX 1.20", dict(fx=1.20)), ("FX 1.40", dict(fx=1.40)), ("host overhead 50%", dict(host=0.5)),
                         ("human time x2", dict(rate=2 * HUMAN_GBP_PER_HOUR)), ("automated (no human)", dict(rate=0))]:
            c2 = sum(run_cost(t, **kw)); print(f"     {name:22s} £{c2:6.2f}  {m(t['price'], c2):5.0%}")
    t5 = dict(mtok=1, cap_min=5, human_min=4)
    for r in (HUMAN_GBP_PER_HOUR, 0):
        c = sum(run_cost(t5, rate=r)); print(f"  £5 test (1M, 5 min, human £{r}/h): cost £{c:.2f} margin {m(5, c):.0%}")
    print("\nCompute (per 8-hour block):")
    for k, r in EC2_USD_PER_HOUR.items():
        e = r * COMPUTE_BLOCK_H / FX_USD_PER_GBP; raw = COMPUTE_FEE + COMPUTE_EC2_MULT * e
        price = round(raw + 0.4999)
        c = e + COMPUTE_HUMAN_MIN / 60 * HUMAN_GBP_PER_HOUR + COMPUTE_EBS_GBP
        c20 = c + 0.2 * e
        print(f"  {k}: EC2 £{e:.2f}; £{COMPUTE_FEE:.0f} + {COMPUTE_EC2_MULT:.0f}x EC2 = £{raw:.2f} -> £{price}; cost £{c:.2f}; margin {m(price, c):.0%}; EC2 +20%: {m(price, c20):.0%}")
    print("\nRepo (per month):")
    for k, (p, h, tool) in REPO.items():
        c = h * HUMAN_GBP_PER_HOUR + tool; print(f"  {k}: £{p}: {h}h x £{HUMAN_GBP_PER_HOUR:.0f} + £{tool} = £{c:.2f}; margin {m(p, c):.0%}; time x2: {m(p, c + h * HUMAN_GBP_PER_HOUR):.0%}")
    print("\nExpert:")
    for k, (p, h, a) in EXPERT.items():
        c = (h + a) * HUMAN_GBP_PER_HOUR; print(f"  {k}: £{p}: ({h}+{a})h x £{HUMAN_GBP_PER_HOUR:.0f} = £{c:.2f}; margin {m(p, c):.0%}; £/h delivered {p / h:.0f}")
