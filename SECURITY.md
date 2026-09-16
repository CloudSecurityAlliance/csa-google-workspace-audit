# Security

## Reporting a vulnerability

Open a [GitHub issue](https://github.com/CloudSecurityAlliance/csa-google-workspace-audit/issues)
for anything that is not itself sensitive. For a finding that should not be public before it is
fixed, email **security@cloudsecurityalliance.org** with `csa-google-workspace-audit` in the subject.

We will acknowledge within five working days. There is no bounty.

## What is in scope

This project is currently an analysis of Google's API surface — there is no `src/`, no released
package and no running service. The security-relevant artifacts are therefore:

- **The domain-wide-delegation scope allowlist** and the reasoning for each scope on it. A scope that
  should not be there, or reasoning that is wrong, is a real finding.
- **The read/write classification** in `analysis/API-SURFACE.md`. A method classified read-safe that
  in fact mutates is a real finding, and the most valuable kind.
- **The setup guidance** in `docs/`. Advice that results in an over-broad grant is a real finding.

## What this project does, and the shape of the risk

A read-only auditor of a Google Workspace tenant, authenticating with a **service account using
domain-wide delegation**. That credential has no ACL ceiling beneath it: it can read every mailbox
and every file in the tenant, and it is a bearer credential — possession alone mints tokens for every
allowlisted scope, against every user, with no further check.

Read-only is enforced in two places by two parties, and only one of them is ours:

1. **In this codebase** — mutating methods are *absent*, not gated, and the `PolicyBackend` seam
   refuses anything undeclared. This is the legibility layer. It is code, and anyone who can edit the
   code can remove it.
2. **On Google's side** — the DWD scope allowlist, editable only by a Workspace super admin. Google
   refuses to mint a token for an unlisted scope. **This is the control that actually holds.**

If you are assessing this project, assess the allowlist first. The code is the weaker half by design.

## Deliberate limitations

`gmail.readonly` is **not** on the phase-1 allowlist ([ADR-001](DECISIONS-ADR/ADR-001.md)) because it
reads every message body in every mailbox, and the stated mail requirement — envelope metadata — needs
`admin.reports.audit.readonly` and no Gmail scope at all. Four Workspace APIs have no read-only scope
whatsoever; where a read is only purchasable with write authority, not offering the read is the
current answer.
