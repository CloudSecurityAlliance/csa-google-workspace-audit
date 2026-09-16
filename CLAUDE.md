# CLAUDE.md

Guidance for AI agents working in this repository.

## What this is, and the one thing that makes it different

A read-only auditor of a Google Workspace tenant. It is the fifth server on the CSA MCP spine
(`Backend (Protocol) → PolicyBackend → Client → mcp/_tools/*`) and the **only one that holds an
admin credential**.

The four predecessors authenticate as the operating user, so Google enforces a ceiling and the
capability layer is defence in depth. This one uses a **service account with domain-wide
delegation**. There is no ceiling: it can read every mailbox and every file in the tenant, and the
key is a bearer credential — possession alone mints tokens.

**Read [`GOALS.md`](GOALS.md) before changing anything.** The short version is below.

## Rules that are not negotiable

**Never add a mutating method.** The 394 mutating methods of the 718 classified in
[`analysis/API-SURFACE.md`](analysis/API-SURFACE.md) are *absent by construction*, not gated. There
is no write path to disable and no gate to misconfigure. If a task appears to require one, the task
is wrong — say so rather than implementing it.

**Never add a scope without an ADR.** The domain-wide-delegation allowlist is the real security
control of this project, not the code. It is editable only by a Workspace super admin, and Google
refuses to mint a token for an unlisted scope. Adding a scope is therefore a security decision that
happens *outside this repository*, where no test can catch it.

**Never treat the client-side `PolicyBackend` as the guarantee.** It exists for legibility — so a
library embedder gets the same refusal an MCP client does, and so failures read as refusals rather
than bare 403s. It is code. Anyone who can edit the code can remove it, **including you**. If you
ever find yourself reasoning "the policy blocks it, so the scope is safe to widen", both controls
are gone.

**Check what a scope *grants*, not what it is *named*.** `gmail.readonly` is honestly read-only and
still reads every message body in every mailbox. Four Workspace APIs have no read-only scope at all —
reading which third-party OAuth apps a user authorised requires the same scope that can turn off
two-step verification domain-wide.

**Probe, don't infer.** Google's published scope lists contradict Google's own capability claims.
Scopes come from the Discovery document's per-method `scopes` array, never from prose. An unprobed
claim is a defect, not a gap.

## Scope boundaries with sibling projects

- **Log reading is this project.** Mail *flow* — who sent what to whom, when — comes from
  `reports.activities.list`, which needs `admin.reports.audit.readonly` and no Gmail scope at all.
- **Mailbox persistence is not.** Filters, forwarding addresses, delegates and send-as are high
  security value and belong to a future `csa-google-gmail-audit`, in the shape GAM occupies today.
  [ADR-001](DECISIONS-ADR/ADR-001.md) defers `gmail.readonly` deliberately; do not re-litigate it by
  adding the scope for convenience.
- **User-credential Gmail and Calendar capability** is
  [`csa-google-gmail-calendar`](https://github.com/CloudSecurityAlliance/csa-google-gmail-calendar),
  which scoped the Admin SDK out and left it here.

## Conventions

Decisions go in [`DECISIONS-ADR.md`](DECISIONS-ADR.md) as an index with one file per decision in
`DECISIONS-ADR/`. A decision is not superseded by editing it — write a new one that says so. Open
work goes in [`TODO.md`](TODO.md), one line per item, with detail in the linked file or GitHub issue.

Fleet-wide standards — library-first, one fail-closed seam, capability coverage within a declared
scope, upstream drift detection, guards proven to fail — are in `surfaces/mcp/GOALS.md` in the
internal CINO-Platform-Engineering repo and are not restated here.

## State

**API surface enumerated; nothing implemented.** There is no `src/`. Do not describe any capability
as working. 260 methods are reachable with a `.readonly` scope and none are built.
