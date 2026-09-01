#!/usr/bin/env python3
"""Derive the operation inventory from the Discovery snapshots in specs/.

Everything downstream — the read/write split, the scope allowlist, the counts in
README.md — is generated from here. Nothing is transcribed from Google's prose:
per-method scopes come from each method's own `scopes` array, which is the artifact
Google generates its client libraries from.

Writes analysis/operation-inventory.csv and prints a summary.
"""
from __future__ import annotations

import csv
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SPECS = ROOT / "specs"
ANALYSIS = ROOT / "analysis"

# A scope Google itself labels read-only. Anchored at the end so that
# `drive.metadata.readonly` matches and a hypothetical `readonly.write` would not.
RO_SCOPE = re.compile(r"(\.readonly|\.read_only|/userinfo\.(email|profile)|\.read)$")

# Methods that mutate despite a non-obvious verb, and reads that use POST.
# Kept explicit and small: the mechanical rules below cover the rest.
READ_VERBS = re.compile(
    r"\.(list|get|search|query|count|check|fetch|lookup|download|export|batchGet|"
    r"aggregate|find|view|.*[Rr]eport)$"
)


def walk(node: dict, api: str, ver: str, out: list, trail: tuple = ()) -> None:
    """Recurse the Discovery resource tree, emitting one row per method."""
    for rname, res in (node.get("resources") or {}).items():
        walk(res, api, ver, out, trail + (rname,))
    for mname, m in (node.get("methods") or {}).items():
        scopes = sorted(m.get("scopes") or [])
        ro = [s for s in scopes if RO_SCOPE.search(s)]
        http = m.get("httpMethod", "")
        mid = m.get("id", ".".join(trail + (mname,)))

        # Classification. The load-bearing question is not "is this a GET" but
        # "can this be reached while holding only a read-only scope" — that is what
        # the domain-wide-delegation allowlist actually constrains.
        looks_read = http == "GET" or bool(READ_VERBS.search(mid))
        if looks_read and ro:
            cls = "READ_SAFE"          # reachable with a .readonly scope
        elif looks_read and not scopes:
            cls = "READ_NO_SCOPE"      # read, but Discovery declares no scope at all
        elif looks_read:
            cls = "READ_NEEDS_RW"      # a read that only a write-capable scope reaches
        else:
            cls = "MUTATING"

        out.append(
            {
                "api": api,
                "version": ver,
                "method_id": mid,
                "resource": ".".join(trail),
                "http": http,
                "path": m.get("path", ""),
                "class": cls,
                "scopes": " ".join(scopes),
                "readonly_scopes": " ".join(ro),
                "description": (m.get("description", "") or "").split("\n")[0][:300],
            }
        )


def main() -> int:
    rows: list[dict] = []
    catalogue: dict[str, dict[str, str]] = {}
    provenance: list[tuple[str, str, str, str]] = []

    for path in sorted(SPECS.glob("*.json")):
        doc = json.loads(path.read_text())
        api, ver = doc.get("name", path.stem), doc.get("version", "")
        walk(doc, api, ver, rows)
        for scope, meta in (
            doc.get("auth", {}).get("oauth2", {}).get("scopes", {}) or {}
        ).items():
            catalogue[scope] = {
                "description": meta.get("description", ""),
                "api": f"{api}:{ver}",
            }
        provenance.append(
            (
                path.name,
                f"{api}:{ver}",
                doc.get("revision", "?"),
                hashlib.sha256(path.read_bytes()).hexdigest(),
            )
        )

    ANALYSIS.mkdir(exist_ok=True)
    rows.sort(key=lambda r: (r["api"], r["version"], r["method_id"]))
    with (ANALYSIS / "operation-inventory.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    with (ANALYSIS / "scope-catalogue.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["scope", "api", "readonly", "description"])
        for s in sorted(catalogue):
            w.writerow(
                [s, catalogue[s]["api"], bool(RO_SCOPE.search(s)), catalogue[s]["description"]]
            )

    with (ANALYSIS / "provenance.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["file", "api", "revision", "sha256"])
        w.writerows(sorted(provenance))

    # ---- summary ----
    by_api: dict[str, dict[str, int]] = {}
    for r in rows:
        k = f"{r['api']}:{r['version']}"
        by_api.setdefault(k, {}).setdefault(r["class"], 0)
        by_api[k][r["class"]] += 1

    print(f"{len(rows)} methods across {len(by_api)} APIs; {len(catalogue)} distinct scopes\n")
    hdr = ("API", "total", "READ_SAFE", "READ_NEEDS_RW", "READ_NO_SCOPE", "MUTATING")
    print(f"{hdr[0]:34}{hdr[1]:>7}{hdr[2]:>11}{hdr[3]:>15}{hdr[4]:>15}{hdr[5]:>10}")
    print("-" * 92)
    for k in sorted(by_api, key=lambda x: -sum(by_api[x].values())):
        c = by_api[k]
        tot = sum(c.values())
        print(
            f"{k:34}{tot:>7}{c.get('READ_SAFE',0):>11}{c.get('READ_NEEDS_RW',0):>15}"
            f"{c.get('READ_NO_SCOPE',0):>15}{c.get('MUTATING',0):>10}"
        )
    print("-" * 92)
    agg = {c: sum(v.get(c, 0) for v in by_api.values()) for c in hdr[2:]}
    print(
        f"{'TOTAL':34}{len(rows):>7}{agg['READ_SAFE']:>11}{agg['READ_NEEDS_RW']:>15}"
        f"{agg['READ_NO_SCOPE']:>15}{agg['MUTATING']:>10}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
