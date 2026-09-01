# API surface — what exists, what is safe to read, what we will never implement

**Status: enumerated, not implemented.** There is no `src/`. Everything below is derived
mechanically from the Discovery snapshots in `specs/` by `scripts/inventory.py`; nothing is
transcribed from Google's prose. Re-run the script rather than editing the numbers.

Generated from 26 Discovery documents fetched 2026-09-01. **709 methods, 175 distinct OAuth
scopes.**

## 1. The one-line answer

Of 709 methods across every Workspace-adjacent API: **388 mutate and will never be
implemented**. Of the 321 that read, **256 are reachable with a scope Google itself labels
`.readonly`** — those are the product. **53 are reads that can only be performed while holding a
write-capable scope**, and they are the whole design problem. 12 declare no scope at all and
need a live probe.

| Class | Methods | Meaning |
|---|---:|---|
| `READ_SAFE` | 256 | Reachable holding only a `.readonly` scope. **Implement.** |
| `READ_NEEDS_RW` | 53 | A read, but the narrowest scope that reaches it can also write. **Decide per case.** |
| `READ_NO_SCOPE` | 12 | Discovery declares no scope. **Probe before trusting.** |
| `MUTATING` | 388 | Creates, updates, deletes. **Never implement.** |

## 2. Per-API breakdown

| API | Total | READ_SAFE | READ_NEEDS_RW | NO_SCOPE | MUTATING | Tier |
|---|---:|---:|---:|---:|---:|---|
| `admin:directory_v1` | 128 | 41 | 5 | 0 | 82 | A |
| `gmail:v1` | 79 | 30 | 0 | 0 | 49 | A |
| `cloudidentity:v1` | 70 | 31 | 1 | 3 | 35 | A |
| `drive:v3` | 64 | 27 | 3 | 0 | 34 | A |
| `chromemanagement:v1` | 58 | 37 | 0 | 5 | 16 | A |
| `cloudsearch:v1` | 49 | 0 | 24 | 0 | 25 | **D — exclude** |
| `calendar:v3` | 38 | 12 | 0 | 0 | 26 | A |
| `vault:v1` | 33 | 11 | 1 | 0 | 21 | A |
| `people:v1` | 24 | 11 | 0 | 0 | 13 | D |
| `meet:v2` | 18 | 15 | 0 | 0 | 3 | A |
| `sheets:v4` | 17 | 3 | 2 | 0 | 12 | D — sibling repo |
| `script:v1` | 16 | 6 | 3 | 0 | 7 | B |
| `workspaceevents:v1` | 15 | 3 | 0 | 4 | 8 | C |
| `chromepolicy:v1` | 14 | 3 | 0 | 0 | 11 | A |
| `gmailpostmastertools:v2` | 14 | 2 | 5 | 0 | 7 | B |
| `tasks:v1` | 14 | 4 | 0 | 0 | 10 | D |
| `alertcenter:v1beta1` | 11 | 0 | 5 | 0 | 6 | **B — no read-only scope exists** |
| `forms:v1` | 10 | 4 | 0 | 0 | 6 | D |
| `keep:v1` | 7 | 3 | 0 | 0 | 4 | C |
| `licensing:v1` | 7 | 0 | 3 | 0 | 4 | **B — no read-only scope exists** |
| `admin:reports_v1` | 6 | 4 | 0 | 0 | 2 | A |
| `admin:datatransfer_v1` | 5 | 4 | 0 | 0 | 1 | A |
| `slides:v1` | 5 | 3 | 0 | 0 | 2 | D — sibling repo |
| `docs:v1` | 3 | 1 | 0 | 0 | 2 | D — sibling repo |
| `groupssettings:v1` | 3 | 0 | 1 | 0 | 2 | **B — no read-only scope exists** |
| `driveactivity:v2` | 1 | 1 | 0 | 0 | 0 | A |

Tiers: **A** implement on read-only scopes · **B** implement only with an accepted write-capable
scope · **C** defer, needs a probe · **D** out of scope for this repo.

## 3. Finding 1 — four APIs have NO read-only scope at all

This is the finding that shapes the design. For these, *reading* requires holding a scope that
can also *destroy*, and the domain-wide-delegation allowlist cannot express the difference.

### `admin.directory.user.security` — the worst trade in the set

Required to read: `tokens.list` / `tokens.get` (**which third-party OAuth apps a user has
authorised** — a first-order audit question), `asps.list` / `asps.get` (app-specific passwords),
`verificationCodes.list`.

Granting it also grants:

| Method | Effect |
|---|---|
| `directory.twoStepVerification.turnOff` | **Disables 2SV on any account in the domain** |
| `directory.users.signOut` | Force sign-out |
| `directory.tokens.delete` | Revoke an app grant |
| `directory.asps.delete` | Delete an app-specific password |
| `directory.verificationCodes.generate` / `.invalidate` | Mint or void backup codes |

To *read* which OAuth apps your users have authorised, the allowlist must carry a scope that can
turn off two-step verification domain-wide. There is no narrower scope. This needs an explicit,
recorded decision — it is the single most consequential line in the whole allowlist.

### `apps.alerts` — Alert Center

All 5 reads (`alerts.list`, `alerts.get`, `getMetadata`, `feedback.list`, `getSettings`) require
`apps.alerts`, which also grants `alerts.delete`, `alerts.batchDelete`, `alerts.undelete` and
`updateSettings`. **Deleting security alerts is an anti-forensic capability**, so this scope on a
key file is a meaningful risk in its own right.

### `apps.groups.settings` — group posting and visibility policy

`groupsSettings.groups.get` reads who may post, who may view members, and whether external
members are allowed. The same scope grants `patch` and `update`.

### `apps.licensing` — license assignment

3 reads; the same scope grants `insert`, `patch`, `update`, `delete`. Lowest stakes of the four,
and the easiest to drop.

**Also in this shape but lower priority:** `script.processes` / `script.metrics` (Apps Script
execution history — genuinely useful for "what automation is running in my tenant"), the
`postmaster*` scopes, and `ediscovery` (needed by `vault.matters.count` alone; every other Vault
read has `ediscovery.readonly`).

## 4. Finding 2 — Gmail is clean, including the mailbox-persistence reads

Worth stating because it is the opposite of what the sibling repo's user-OAuth findings would
lead you to expect. **`gmail.readonly` reaches every settings read we care about**:

`settings.filters.list` · `settings.delegates.list` · `settings.forwardingAddresses.list` ·
`settings.getAutoForwarding` · `settings.sendAs.list` · `settings.cse.keypairs.list`

So the canonical post-compromise persistence check — *is there a filter quietly forwarding this
mailbox offsite, and who else can read it* — is fully answerable with a read-only scope. The
corresponding writes (`filters.create`, `forwardingAddresses.create`, `updateAutoForwarding`,
`delegates.create`) sit behind `gmail.settings.basic` / `gmail.settings.sharing`, which simply
never go on the allowlist.

## 5. Finding 3 — Cloud Search is 49 methods and 24 read-traps; exclude it

Every Cloud Search read requires `cloud_search` or a `cloud_search.*` scope, none of which are
read-only, and several of which (`cloud_search.indexing`, `cloud_search.settings`) can rewrite a
search index. It contributes 24 of the 53 traps by itself. Unless CSA actually runs Cloud Search,
excluding it removes nearly half the problem for no loss.

## 6. Finding 4 — 12 methods declare no scope in Discovery

`chromemanagement.customers.connectorConfigs.{get,list}` ·
`chromemanagement.customers.certificateProvisioningProcesses.*` ·
`chromemanagement.operations.list` · `cloudidentity.customers.userinvitations.{get,list,isInvitableUser}` ·
`workspaceevents.tasks.*`

An absent `scopes` array means the snapshot cannot tell us what these need. Per the house rule
that a probe beats documentation, these get a live call before any of them is implemented.

## 7. The proposed allowlist

`analysis/dwd-scope-allowlist.txt`, generated by `scripts/scope_allowlist.py`. **35 read-only
scopes** cover every read-only-reachable method across the Tier A/B APIs, out of 47 candidates.

The generated list is minimal *by count*, not *by privilege* — greedy set cover prefers the
broad scope because it covers more methods. `drive.readonly` covers 26 methods, but a sharing
audit may only need `drive.metadata.readonly`. **Narrowing is a human judgement and has not been
done yet.**

## 8. What this repo does not cover

- **Docs / Sheets / Slides content** — [`csa-google-workspace`](https://github.com/CloudSecurityAlliance/csa-google-workspace).
- **Gmail / Calendar as a user-facing product** — `csa-google-gmail-calendar`, which explicitly
  scoped the Admin SDK out and left it to this repo. Gmail and Calendar appear here only as
  *audit reads performed by impersonation*, which is a different credential model and a
  different tool surface.
- **Mail flow — "who sent and received what."** Requested, and **not resolved by this pass.**
  Admin SDK Reports `activities.list` covers admin, login, drive, calendar, token, groups, saml,
  chrome and meet — but message-level Gmail log events do not appear in the Reports API. The
  likely answers are Vault (`ediscovery.readonly`, 11 read methods, already Tier A) and the Gmail
  log BigQuery export, which is not a Discovery API at all. **Open question, tracked.**
