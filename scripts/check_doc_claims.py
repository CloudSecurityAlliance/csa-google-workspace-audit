#!/usr/bin/env python3
"""Assert the counts written in the prose still match the generated inventory.

This exists because it already went wrong. The classifier was corrected after
`analysis/API-SURFACE.md` was written (dropping `resolve` from the read-verb list, because
`drive.accessproposals.resolve` mutates), and three commits shipped with 256/53/388 in the
prose against 255/52/390 in the data. Nothing caught it. The docs ARE the design record
here, so a stale sentence is what the next decision gets built on.

Two rules, inherited from `csa-google-workspace`'s version of this script:

  1. ENUMERATE REALITY AND COMPARE. Never ask "is the right string present" - that is how a
     stale claim survives a repeatedly refreshed "last verified" date.
  2. AN EMPTY COLLECTION IS A FAILURE, not a pass. A loop that asserts nothing because it
     found nothing to assert is the failure mode this file is built to avoid, so every
     extractor below declares how many claims it expects to find.

Exit 0 = every claim matches. Exit 1 = drift. Run it before committing prose.
"""
from __future__ import annotations

import collections
import csv
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CLASSES = ("READ_SAFE", "READ_NEEDS_RW", "READ_NO_SCOPE", "MUTATING")

# Historical notes are wrapped in *( ... )* and are deliberately exempt: recording what a
# document used to get wrong must stay compatible with asserting what is true now.
HISTORICAL = re.compile(r"\*\([^)]*\)\*", re.S)


def truth() -> tuple[dict[str, dict[str, int]], dict[str, int], int]:
    rows = list(csv.DictReader((ROOT / "analysis" / "operation-inventory.csv").open()))
    if not rows:
        sys.exit("operation-inventory.csv is empty - run scripts/inventory.py")
    per_api: dict[str, dict[str, int]] = collections.defaultdict(collections.Counter)
    totals: collections.Counter = collections.Counter()
    for r in rows:
        per_api[f"{r['api']}:{r['version']}"][r["class"]] += 1
        totals[r["class"]] += 1
    return per_api, dict(totals), len(rows)


def read(name: str) -> str:
    return HISTORICAL.sub("", (ROOT / name).read_text())


def main() -> int:
    per_api, totals, n_methods = truth()
    fails: list[str] = []
    checked = 0

    def eq(label: str, claimed: int, actual: int) -> None:
        nonlocal checked
        checked += 1
        if claimed != actual:
            fails.append(f"{label}: doc says {claimed}, inventory says {actual}")

    # --- per-API tables: | `api:ver` | total | safe | needs_rw | no_scope | mutating | tier |
    row6 = re.compile(
        r"^\|\s*`([^`]+)`\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|",
        re.M,
    )
    found_api_rows = 0
    for doc in ("analysis/API-SURFACE.md",):
        for m in row6.finditer(read(doc)):
            api = m.group(1)
            if api not in per_api:
                fails.append(f"{doc}: table names unknown API `{api}`")
                continue
            found_api_rows += 1
            got, c = [int(g) for g in m.groups()[1:]], per_api[api]
            eq(f"{doc} `{api}` total", got[0], sum(c.values()))
            for i, cls in enumerate(CLASSES):
                eq(f"{doc} `{api}` {cls}", got[i + 1], c[cls])
    if found_api_rows != len(per_api):
        fails.append(
            f"per-API table covers {found_api_rows} APIs, inventory has {len(per_api)}"
        )

    # --- class-summary tables: | `READ_SAFE` | 255 | ... and | Mutating | 390 | ...
    label_to_class = {
        "READ_SAFE": "READ_SAFE", "Reachable with a `.readonly` scope": "READ_SAFE",
        "READ_NEEDS_RW": "READ_NEEDS_RW", "A read that needs a write-capable scope": "READ_NEEDS_RW",
        "READ_NO_SCOPE": "READ_NO_SCOPE", "No scope declared in Discovery": "READ_NO_SCOPE",
        "MUTATING": "MUTATING", "Mutating": "MUTATING",
    }
    row2 = re.compile(r"^\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|", re.M)
    found_class_rows = 0
    for doc in ("analysis/API-SURFACE.md", "README.md"):
        for m in row2.finditer(read(doc)):
            cls = label_to_class.get(m.group(1).strip().strip("`"))
            if cls:
                found_class_rows += 1
                eq(f"{doc} {m.group(1).strip()}", int(m.group(2)), totals[cls])
    if found_class_rows < 8:
        fails.append(f"expected >=8 class-summary rows across the docs, found {found_class_rows}")

    # --- prose totals
    prose = re.compile(
        r"Of (\d+) methods across every Workspace-adjacent API: \*\*(\d+) mutate.*?"
        r"Of the (\d+) that read, \*\*(\d+) are reachable.*?\*\*(\d+) are reads that can only",
        re.S,
    )
    m = prose.search(read("analysis/API-SURFACE.md"))
    if not m:
        fails.append("API-SURFACE.md: the prose-totals sentence no longer matches its pattern")
    else:
        n_read = totals["READ_SAFE"] + totals["READ_NEEDS_RW"] + totals["READ_NO_SCOPE"]
        eq("prose total methods", int(m.group(1)), n_methods)
        eq("prose MUTATING", int(m.group(2)), totals["MUTATING"])
        eq("prose reads", int(m.group(3)), n_read)
        eq("prose READ_SAFE", int(m.group(4)), totals["READ_SAFE"])
        eq("prose READ_NEEDS_RW", int(m.group(5)), totals["READ_NEEDS_RW"])

    # --- allowlist size, claimed in both docs and in ADR-001
    live = [
        ln.split()[0]
        for ln in (ROOT / "analysis" / "dwd-scope-allowlist.txt").read_text().splitlines()
        if ln.startswith("https://")
    ]
    if not live:
        fails.append("dwd-scope-allowlist.txt lists no active scopes")
    allowlist_claim = re.compile(
        r"phase-1\s+(?:allowlist|list)\s+is\s+\**(\d+)\**\s*(?:read-only\s+)?scopes", re.I
    )
    found_allowlist = 0
    for doc in ("README.md", "analysis/API-SURFACE.md", "DECISIONS-ADR/ADR-001.md"):
        for m in allowlist_claim.finditer(read(doc)):
            found_allowlist += 1
            eq(f"{doc} allowlist size", int(m.group(1)), len(live))
    if found_allowlist < 3:
        fails.append(
            f"expected an allowlist-size claim in each of the 3 documents, found {found_allowlist}"
        )

    # --- distinct-scope catalogue size, claimed separately from the allowlist
    n_scopes = sum(1 for _ in csv.DictReader((ROOT / "analysis" / "scope-catalogue.csv").open()))
    found_cat = 0
    for doc in ("README.md", "analysis/API-SURFACE.md"):
        pat = re.compile(r"(\d+)\s+distinct\s+(?:OAuth\s+)?scopes|(\d+)\s+scopes,\s+each\s+flagged")
        for m in pat.finditer(read(doc)):
            found_cat += 1
            eq(f"{doc} scope catalogue size", int(m.group(1) or m.group(2)), n_scopes)
    if not found_cat:
        fails.append("no scope-catalogue-size claim found")

    print(f"{checked} claims checked against {n_methods} methods and {len(live)} live scopes")
    if fails:
        print(f"\n{len(fails)} DRIFTED:")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("OK - every documented count matches the generated data")
    return 0


if __name__ == "__main__":
    sys.exit(main())
