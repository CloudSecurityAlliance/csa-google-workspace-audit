# Security Resources

The security surface of this project: what it exposes, to whom, and how it is protected.

**Last reviewed:** 2026-09-16 · **Next review:** 2026-12-16

## Summary

There is **no network surface**. This is a local stdio MCP server and a Python library, run by an
operator on their own machine — nothing listens, nothing is deployed, and there is no hosted
endpoint. The exposure is therefore not a port; it is **a credential and a published artifact**.

That credential is a Google service account with domain-wide delegation, which can read every mailbox
and every file in the CSA tenant. It is the most privileged credential in the CSA MCP fleet, held by
the least-built project.

## Exposure surface inventory

| Surface | Type | Exposure tier | Cloudflare | Auth | Notes |
|---|---|---|---|---|---|
| `github.com/CloudSecurityAlliance/csa-google-workspace-audit` | public repo | `public-unauthed` | n/a | none | Source, the API classification, and the setup guidance. Contains no credentials and no CSA tenant identifiers — verified 2026-09-15 |
| Local stdio MCP server | process on an operator's machine | `internal-staff` | n/a | inherits the operator's shell | Not reachable over a network. No listener |
| PyPI package | published artifact | `public-unauthed` | n/a | n/a | **Not yet published.** When it is, `PUBLIC-GITHUB-REPO-STANDARDS.md` applies: Trusted Publishing, attestations, SHA-pinned actions |
| Google Workspace APIs | outbound only | n/a | n/a | service account + DWD | The actual risk. See below |

**Cloudflare is not applicable** to any row, because no row is a CSA-operated inbound surface. That
is an explicit finding rather than an omission.

## Access model

The service-account key is a **bearer credential**: possession alone mints tokens, for every scope on
the domain-wide-delegation allowlist, against every user in the tenant, with no interactive consent
and no per-user check. There is no ACL ceiling beneath it, unlike every sibling project, which
authenticate as the operating user.

Read-only therefore rests on **the allowlist, not the code**. Google refuses to mint a token for an
unlisted scope, and only a Workspace super admin can change the list. The client-side `PolicyBackend`
refusal is defence in depth and legibility; it is removable by anyone who can edit the repository,
which by design includes an AI agent.

The phase-1 allowlist is 34 scopes, every one `.readonly`, each with a recorded reason.
`gmail.readonly` is deliberately excluded ([ADR-001](DECISIONS-ADR/ADR-001.md)).

## Known gaps and accepted risks

| Gap | Status | Owner |
|---|---|---|
| **No branch protection, no required CI gates, no SHA-pinned actions.** Public since 2026-09-15 with none of `PUBLIC-GITHUB-REPO-STANDARDS.md` applied | Open — tracked in `TODO.md` | Kurt Seifried |
| **Allowlist drift is undetectable from here.** The live allowlist lives in the Google admin console; nothing in this repo can compare it to the documented one | Open — no mechanism designed | Kurt Seifried |
| **One reviewer for allowlist changes.** A super-admin change with a single approver | Open | Kurt Seifried |
| **The classification is a point-in-time snapshot.** 709 methods classified on one date; a method that becomes mutating is invisible until re-probed | Open — [CINO-PE #49](https://github.com/CloudSecurityAlliance-Internal/CINO-Platform-Engineering/issues/49) | Kurt Seifried |
| **Four APIs have no read-only scope at all.** Reading third-party OAuth grants needs the scope that disables two-step verification domain-wide | Accepted — those reads are not offered | Kurt Seifried |

## Data classification

This project **stores nothing**. Reads are served live and there is no cache, index or event store,
so there is no `DATA-RESOURCES.md` — an explicit N/A rather than an omission. The data it *reaches*
is the entire CSA tenant, including PII and message metadata, which is why the credential rather than
the storage is the thing to assess.
