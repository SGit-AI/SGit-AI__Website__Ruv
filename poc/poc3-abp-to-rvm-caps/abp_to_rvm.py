#!/usr/bin/env python3
"""POC3: ABP -> RVM capability rights per role, and the gap report.
RVM (github.com/ruvnet/rvm): unforgeable capabilities with 7 rights READ, WRITE, GRANT, REVOKE, EXECUTE, PROVE, GRANT_ONCE; no ambient authority.
Usage: python3 abp_to_rvm.py [abp.json] > rvm-caps.md"""
import json, sys, pathlib
root = pathlib.Path(__file__).resolve().parents[2]
abp = json.load(open(sys.argv[1] if len(sys.argv) > 1 else root / "abp/examples/ruflo-sparc-swarm.abp.json"))
m = json.load(open(root / "abp/mapping.json"))["primitives"]
print(f"# RVM capabilities compiled from the ABP: {abp['deployment']}\n\nOwner: {abp['owner']} · valid until {abp.get('valid_until','?')}\n")
gaps = []
for role in abp["roles"]:
    grant, withheld = set(), []
    for row in role["rows"]:
        rights = m.get(row["capability"], {}).get("rvm", [])
        if row["mandate"] == "yes": grant |= set(rights)
        elif row["reach"]: withheld.append((row["capability"], row["mandate"], row.get("barrier", "")))
        if row["reach"] and row["mandate"] != "yes" and not row.get("barrier"): gaps.append((role["id"], row["capability"]))
    print(f"## {role['id']}: {role['purpose']}\n\nCapability token rights: `{', '.join(sorted(grant)) or 'none'}` (GRANT never delegated unless a row says so)\n")
    if withheld:
        print("| reachable but not mandated | mandate | barrier |\n|---|---|---|")
        for c, md, b in withheld: print(f"| {c} | {md} | {b or '**NONE: gap**'} |")
        print()
print(f"## Gaps\n\n{len(gaps)} rows have reach, no mandate and no barrier." + "".join(f"\n- {r}: {c}" for r, c in gaps))
print("\nNote: RVM rights are coarser than ABP primitives (EXECUTE covers both a sandboxed test run and an email send). The ABP keeps the distinction; the token alone cannot. That is the argument for compiling tokens FROM a mandate.")
