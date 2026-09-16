# TODO — csa-google-workspace-audit

Index of **all** open work, one line per item, per the CINO todo-index convention. Detail lives in
the linked file or GitHub issue; nothing else needs searching.

Created 2026-09-16.

## Repo standards

- [ ] **Apply [`PUBLIC-GITHUB-REPO-STANDARDS.md`](https://github.com/CloudSecurityAlliance-Internal/CINO-Platform-Engineering/blob/main/PUBLIC-GITHUB-REPO-STANDARDS.md).**
  This repository went public on 2026-09-15 with none of it configured: no branch protection, no
  required CI gates, no SHA-pinned actions. It has no CI at all yet.
- [ ] **Decide vendored versus fetched Discovery snapshots.** ~5 MB of Google's own specs live in
  `specs/`. They are upstream artifacts and they drift. Wants an ADR either way.

## Drift

- [ ] **Nothing watches the upstream surface** *automatically* —
  [CINO-PE #49](https://github.com/CloudSecurityAlliance-Internal/CINO-Platform-Engineering/issues/49).
  Run once by hand on 2026-09-16 ([API-SURFACE §11](analysis/API-SURFACE.md#11-finding-6--the-first-re-classification-found-no-scope-change-anywhere)):
  23 of 26 revisions moved, 9 methods arrived, **0 scope arrays changed**, allowlist unchanged. The
  diff is mechanical and wants to be CI, not a person remembering. Compare *canonical* digests —
  Google reorders JSON keys, so raw sha256 reports drift that is not there.
- [ ] **Re-probe for an official Google admin MCP server.** Absent as of 2026-09-16
  ([`docs/OFFICIAL-MCP-SERVERS.md`](docs/OFFICIAL-MCP-SERVERS.md)); `adminmcp.googleapis.com`
  appearing would change the build/buy case for this repo.

## Build

- [ ] **Implement the 260 methods reachable with a `.readonly` scope.** None are built. Ordering and
  rationale in [`GOALS.md`](GOALS.md).
- [ ] **Probe the 12 methods for which Discovery declares no scope.** Probe before assuming either way.
- [ ] **Decide the 52 case-by-case methods** — reads that require a write-capable scope. 24 are Cloud
  Search and already excluded; the rest need a per-case decision and the default is no.

## Allowlist governance

- [ ] **Get a second reviewer for the DWD scope allowlist.** It is a Workspace super-admin change and
  the real security control of the project; one reviewer is the wrong number.
- [ ] **Decide how an allowlist change is noticed.** It happens in the Google admin console, where
  this repository cannot see it, so nothing here can detect drift between the documented allowlist
  and the live one.
