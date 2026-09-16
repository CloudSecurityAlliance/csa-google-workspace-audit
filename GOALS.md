# Goals

Shared goals for CSA's MCP server fleet — library-first, local stdio, one fail-closed seam at the
data boundary, offline-testable — are stated once in the fleet roster (`surfaces/mcp/ROSTER.md` in
the internal CINO-Platform-Engineering repo) and are not restated here. This project sits on the
same spine as its four predecessors: `Backend (Protocol) → PolicyBackend → Client → mcp/_tools/*`.

**One thing here is not shared, and it is the reason this file exists.**

## North Star

A CSA administrator can ask *who exists, who is privileged, what is shared with whom, who can read
whose mail, and what happened* — and get an answer from a tool that **cannot** do anything else,
where "cannot" is guaranteed by Google rather than by this codebase.

## The difference that sets everything else

The four predecessors authenticate as the operating user. Every call runs under that user's own
ACLs, so the capability layer is a ceiling *below* what Google already permits — and if the gate
failed open, the blast radius is still one user's own access.

This server uses a **service account with domain-wide delegation**. There is no ceiling underneath
it: it can read every mailbox and every file in the tenant. The service-account key is a bearer
credential — possession alone mints tokens.

So read-only is enforced **twice, by two different parties**:

1. **In the client** — the `PolicyBackend` seam, as in every sibling. Necessary and *not sufficient*:
   it is code, and anyone who can edit the code can remove it. Including an AI.
2. **On Google's side** — the domain-wide-delegation scope allowlist, editable only by a Workspace
   super admin. Google refuses to mint a token for an unlisted scope, so a client rewritten to
   request `gmail.modify` gets nothing back.

**The second is the real control, and the allowlist is therefore the security artifact of this
project.** The first exists so a library embedder gets the same guarantee an MCP client does, and so
failures are legible rather than bare 403s.

Everything below follows from that.

## Near-term

| Goal | Success metric |
|---|---|
| **Read-only by construction, not by policy** | The 390 mutating methods are absent from the client, not gated in it. There is no write path to disable, no gate to misconfigure, and no wrapper to bypass |
| **The allowlist stays minimal and justified** | Every scope on the phase-1 allowlist is `.readonly` and has a recorded reason. 34 today. A scope is added by ADR or not at all |
| **Implement the 255 reachable methods** | The methods reachable with a `.readonly` scope, as classified in [`analysis/API-SURFACE.md`](analysis/API-SURFACE.md). None are built yet |
| **Probe the 12 with no declared scope** | Discovery declares no scope for twelve methods. Probe before assuming either way |
| **A second pair of eyes on the allowlist** | The allowlist is a Workspace super-admin change and a single reviewer is the wrong number for it |

## Medium-term

- **Decide the 52 case-by-case methods.** Reads that require a write-capable scope. Twenty-four are
  Cloud Search and already excluded; the rest need a per-case decision, and the default is no.
- **Name the four APIs with no read-only scope at all, prominently.** Reading which third-party OAuth
  apps a user has authorised requires `admin.directory.user.security` — *the same scope that can turn
  off two-step verification domain-wide*. Alert Center reads require `apps.alerts`, which can delete
  alerts. Also `apps.groups.settings` and `apps.licensing`. Where a read is only purchasable with
  write authority, the honest answer may be not to offer the read.
- **Apply `PUBLIC-GITHUB-REPO-STANDARDS.md`.** Public since 2026-09-15 with none of it configured —
  no branch protection, no required CI gates, no SHA-pinned actions.
- **Decide vendored versus fetched Discovery snapshots.** ~5 MB of Google's own specs live in
  `specs/`. They are upstream artifacts and they drift.

## Long-term

- **Continuous tenant posture, not one-off answers.** The same reads, on a schedule, with changes
  surfaced — which is the audit question asked continuously rather than when someone remembers.
- **A hosted deployment is genuinely available here, and only here.** This is the one sibling whose
  credential is CSA's rather than a user's, so hosting would not change whose credential it acts
  with. That makes it the fleet's natural first hosted instance — and also the one where getting it
  wrong is worst.

## Non-goals

Named so they are decisions rather than drift.

- **The 390 mutating methods. Ever.** Not gated, not off-by-default, not behind a profile — absent.
- **`gmail.readonly` in phase 1** ([ADR-001](DECISIONS-ADR/ADR-001.md)). It reads every message body
  in every mailbox, and the stated mail requirement — envelope metadata, the equivalent of Email Log
  Search — needs only `admin.reports.audit.readonly`, with no Gmail scope and no impersonation.
- **Remediation.** This answers what is true. Changing it is a different tool with a different
  credential and a different conversation.
- **Being a SIEM.** Reads are served live; nothing is persisted and there is no event store.

## How we would know this failed

1. **A scope is added without an ADR.** The allowlist is the real control, so allowlist drift *is*
   the security failure — and it happens in the Google admin console, where this repo cannot see it.
2. **The client-side gate is treated as the guarantee.** It is the legibility layer. The moment
   anyone reasons "the policy blocks it, so we can widen the scope", both controls are gone.
3. **`gmail.readonly` arrives quietly** to enable one convenient feature, and every message body in
   CSA becomes reachable by whoever holds the key.
4. **The classification goes stale.** 709 methods across 26 APIs were classified on one date. Google
   ships. A method that became mutating, or a new one that arrived, is invisible until re-probed.
5. **The service-account key is treated as a secret rather than as a credential.** Possession mints
   tokens for every scope on the allowlist, against every user in the tenant, with no further check.

## Who benefits

- **CSA** — the security questions about its own tenant become answerable by an agent rather than by
  clicking through the admin console, which is why they currently go unanswered.
- **The community** — public, and the read/write classification of 709 Workspace methods is useful
  to anyone auditing a tenant, whether or not they run this client.
- **The fleet** — this is where the rule *enforcement an AI can edit is not enforcement* was reached
  by building rather than by argument.
