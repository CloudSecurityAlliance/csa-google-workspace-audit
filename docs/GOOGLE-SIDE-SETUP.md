# Google-side setup — enforcing read-only where the client cannot be trusted

This document is the operator's half of the security model. The client in this repository will
enforce read-only too, but **that enforcement is advisory**: it is code, and anyone who can edit
the code — including an AI agent asked to "just add a delete tool" — can remove it. Everything
below is enforced by Google, outside this repository, and changeable only by a Workspace super
admin.

Setup is deliberately not one-click. The audience is Workspace administrators.

## The four controls, strongest first

| # | Control | Enforced at | Who can change it |
|---|---|---|---|
| 1 | **DWD scope allowlist** | Token mint — an unlisted scope yields no token | Super admin |
| 2 | **Custom admin role** on the impersonated admin | API call — 403 regardless of scope | Super admin |
| 3 | **App access control** (Trusted/Limited/Blocked) | Token mint | Super admin |
| 4 | **Cloud project API enablement** | API call — `SERVICE_DISABLED` | Project owner |

Control 1 is the load-bearing one. Controls 2–4 are defence in depth.

## Step 1 — Google Cloud: project and service account

A service account is a **Google Cloud** resource, not a Workspace user. It consumes no license,
has no mailbox, and does not appear in your Directory.

1. Create a dedicated GCP project, so the enabled-API list belongs to this tool alone.
2. Enable only the APIs in `analysis/API-SURFACE.md` Tier A/B — `admin`, `drive`,
   `driveactivity`, `gmail`, `calendar`, `vault`, `cloudidentity`, `chromemanagement`,
   `chromepolicy`, `meet`. **Do not enable `cloudsearch`** (Finding 3).
3. Create a service account. Note its **numeric OAuth client ID** (21 digits, on the details
   page) — that, not the email, is what the Admin console asks for.
4. Create a JSON key.

> **Blocker to check first:** if the GCP organisation enforces
> `constraints/iam.disableServiceAccountKeyCreation`, step 4 fails and the project needs an
> exemption.

## Step 2 — Admin console: the scope allowlist

Security → Access and data control → API controls → Domain-wide delegation → **Manage Domain
Wide Delegation** → Add new.

Paste the client ID from step 1 and the comma-joined scope list from the bottom of
`analysis/dwd-scope-allowlist.txt` (regenerate with `python3 scripts/scope_allowlist.py`).

**This page is the security boundary.** It is readable at any time and shows exactly what this
tool may do across the tenant. If every entry ends in `.readonly`, no amount of editing the
client can make it write.

### The lines that are not `.readonly`

Four capabilities cannot be had read-only. Each is a deliberate decision, not an oversight —
`analysis/API-SURFACE.md` §3 has the full cost of each.

| Scope | Buys you | Also grants |
|---|---|---|
| `admin.directory.user.security` | Which OAuth apps each user authorised | **Turn off 2SV**, force sign-out, revoke tokens |
| `apps.alerts` | Alert Center alerts | **Delete alerts** (anti-forensic) |
| `apps.groups.settings` | Group posting/visibility policy | Rewrite that policy |
| `apps.licensing` | License assignments | Assign and revoke licenses |

Default recommendation: **omit all four initially.** Add back only with a written decision
recording what the audit needs it for.

## Step 3 — Admin console: a read-only custom admin role

Admin SDK calls are gated by the scope *and* by the privileges of the impersonated account. This
is a second, independent fence — but only for the Admin SDK surfaces, never for per-user data.

Account → Admin roles → Create new role, granting only read privileges (Users: Read, Groups:
Read, Organizational Units: Read, Reports, Security: Read). Assign it to a dedicated,
non-human account — not to a person's login — and point impersonation at that account.

> **To verify:** Google now permits assigning admin roles **directly to a service account**,
> removing impersonation from the Admin SDK path entirely. If it covers our APIs it is strictly
> better than a stand-in admin account. Not yet probed — see `analysis/API-SURFACE.md`.

## Step 4 — App access control

Security → Access and data control → API controls → Manage third-party app access. Configure the
OAuth client as **Limited** to the allowlisted scopes.

## The asymmetry to understand before you start

| Surface | Impersonates | Second fence? |
|---|---|---|
| Admin SDK (Directory, Reports, Alert Center) | a read-only admin account | **Yes** — the custom role |
| Per-user data (Alice's Drive sharing, Gmail filters, Calendar ACL) | `alice@example.org` | **No** — allowlist only |

For per-user reads the allowlist is the only thing between this tool and a mutation, because
impersonating Alice inherits Alice's ordinary rights over her own data — and Alice may write her
own filters. That asymmetry is why the allowlist gets the scrutiny.

## Key custody

The JSON key **is** the credential. No browser step, no consent screen, no second factor:
possession alone mints tokens as any user in the tenant, up to the allowlist.

- `chmod 0600`, outside the repository.
- Never committed — `.gitignore` covers the known shapes, but a Google key downloads as
  `<project>-<12 hex>.json`, which is easy to add by accident. Check `git status` before staging.
- **Rotate on a schedule with a named owner and a date.**
- A leaked key against a `.readonly` allowlist is a serious data-exposure incident. Against write
  scopes it is tenant-wide compromise. That difference is the whole argument for §2.
