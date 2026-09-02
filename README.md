# csa-google-workspace-audit

```
project_tracker_base: CINO Project Tracker:appf7fRQUvY9Iy7sL
project_tracker_table: Projects:tblchmbxSAavvJKaY
project_tracker_record: TODO - not yet created
project_source: github:CloudSecurityAlliance-Internal/CINO-Projects/projects/CloudSecurityAlliance/csa-google-workspace-audit
```

A Python library and local stdio MCP server for **read-only auditing of a Google Workspace
tenant** — who exists, who is privileged, what is shared with whom, who can read whose mail, and
what happened.

> **Status: API surface enumerated. Nothing implemented.** There is no `src/`. This repository
> currently holds the upstream Discovery snapshots, the operation inventory, the read/write
> classification, and the generated scope allowlist. Do not describe any feature below as working.

## Scope

**709 methods across 26 Workspace APIs.** 388 of them mutate and **will never be implemented**.

| Class | Methods | Disposition |
|---|---:|---|
| Reachable with a `.readonly` scope | 256 | Implement |
| A read that needs a write-capable scope | 53 | Decide per case; 24 are Cloud Search, excluded |
| No scope declared in Discovery | 12 | Probe first |
| Mutating | 388 | **Never implement** |

Full per-API table and tiers: [`analysis/API-SURFACE.md`](analysis/API-SURFACE.md).

**The phase-1 allowlist is 34 scopes, every one of them `.readonly`.** `gmail.readonly` is
deliberately not among them ([ADR-001](DECISIONS-ADR/ADR-001.md)) — it reads every message body
in every mailbox, and mail flow does not need it.

## Why this exists

Fifth in the line after [`csa-skilljar`](https://github.com/CloudSecurityAlliance/csa-skilljar),
[`csa-google-workspace`](https://github.com/CloudSecurityAlliance/csa-google-workspace),
`csa-zendesk` and `csa-google-gmail-calendar`, on the same spine:

```
Backend (Protocol)   the seam - keyword-only args, returns raw upstream envelopes
    ^ wrapped by
PolicyBackend        capability gating; FAILS CLOSED - an ungated method is refused
    ^ consumed by
Client               thin typed library surface (the public product)
    ^ consumed by
mcp/_tools/*.py      per-family register_*(app, get_client) producers
```

`csa-google-gmail-calendar` scoped the Admin SDK out explicitly — *"out of scope, each needing
its own snapshot"* — and left it here.

**It differs from all four predecessors in one way that changes everything.** They authenticate
as the operating user, so every call runs under that user's own ACLs and the capability layer is
a ceiling *below* what Google already permits. This server uses a **service account with
domain-wide delegation**, which has no such ceiling: it can read every mailbox and every file in
the tenant. There is nothing underneath it.

So read-only is enforced **twice, in two different places, by two different parties**:

1. **In the client** — the `PolicyBackend` seam, as in every sibling. Necessary, and *not
   sufficient*: it is code, and anyone who can edit the code can remove it. Including an AI.
2. **On Google's side** — the domain-wide-delegation scope allowlist, editable only by a
   Workspace super admin. Google refuses to mint a token for an unlisted scope, so a client
   rewritten to request `gmail.modify` gets nothing back.

The second is the real control. The first exists so that a library embedder gets the same
guarantee an MCP client does, and so that failures are legible rather than 403s.

## Three findings that shape the design

- **Four APIs have no read-only scope at all.** Reading which third-party OAuth apps a user has
  authorised requires `admin.directory.user.security` — the same scope that can **turn off
  two-step verification** domain-wide. Alert Center reads require `apps.alerts`, which can
  **delete alerts**. Also `apps.groups.settings` and `apps.licensing`. Current recommendation is
  to omit all four and add back only by written decision. ([§3](analysis/API-SURFACE.md))
- **Gmail is clean.** `gmail.readonly` reaches `settings.filters.list`,
  `settings.delegates.list`, `settings.forwardingAddresses.list` and `getAutoForwarding` — so the
  canonical mailbox-persistence audit is fully answerable read-only.
- **Cloud Search contributes 24 of the 53 read-traps by itself** and is excluded.
- **Reading Gmail settings costs domain-wide mailbox read.** The narrowest read-only scope
  reaching `settings.filters.list` is `gmail.readonly`, which also reads every message body in
  every mailbox; the alternative, `gmail.settings.basic`, can *write* filters. So the
  mailbox-persistence audit and the mail-flow log are separable decisions — the latter needs no
  Gmail scope at all. ([§10](analysis/API-SURFACE.md))

## What is here

| Path | What |
|---|---|
| `specs/` | 26 upstream Discovery snapshots + `PROVENANCE.md` (URLs, revisions, sha256) |
| `analysis/API-SURFACE.md` | **Start here.** The enumeration, the tiers, the four findings |
| `analysis/operation-inventory.csv` | 709 rows, one per method, with scopes and classification |
| `analysis/scope-catalogue.csv` | 175 scopes, each flagged read-only or not |
| `analysis/dwd-scope-allowlist.txt` | **Generated.** Paste into the Admin console |
| `docs/GOOGLE-SIDE-SETUP.md` | The operator's half: the four Google-side controls, and key custody |
| `DECISIONS-ADR.md` | Decision log index; entries in `DECISIONS-ADR/` |
| `scripts/fetch_specs.sh` | Re-fetches `specs/` |
| `scripts/inventory.py` | Regenerates the inventory and the catalogue |
| `scripts/scope_allowlist.py` | Regenerates the allowlist |

```bash
./scripts/fetch_specs.sh && python3 scripts/inventory.py && python3 scripts/scope_allowlist.py
```

## Open questions

- **Mail flow is resolved: `reports.activities.list(applicationName="gmail")`** — the API
  equivalent of console Email Log Search, under `admin.reports.audit.readonly`, needing no Gmail
  scope and no impersonation. Still to probe: the licence gate, the retention window (~30 days),
  and the event parameter names, which Discovery types generically.
- **Admin roles assigned directly to a service account**, removing impersonation from the Admin
  SDK path. Believed to exist; not probed.
- **12 methods declare no scope** in Discovery and need a live call.

## License

Apache 2.0.
