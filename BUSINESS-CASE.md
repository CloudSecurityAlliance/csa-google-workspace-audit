# Business Case

## Executive summary

CSA cannot currently answer basic security questions about its own Google Workspace tenant — who is
privileged, what is shared outside the organisation, who can read whose mail, what happened — without
a person clicking through the admin console. That is why those questions mostly go unanswered.

There is **no official Google MCP server for the admin surface at all**. Google ships MCP servers for
Gmail and Calendar as an end user; nothing exists for tenant administration. The established prior
art is GAM, a command-line tool: capable, and the wrong shape for an agent, because it assumes a
human driving it and grants whatever the admin already has.

This project makes the tenant answerable by an agent, and does it **read-only by construction** —
which is the part that makes it safe enough to point at a credential that can read every mailbox in
CSA.

**Benefit categories:** Required / Compliance (primary) · Synergy (primary) · Research / Exploration
(secondary)

## CSA value

**The questions get asked because asking becomes cheap.** Five distinct questions about CSA's own
estate arose in a single week during 2026-08 — which integrations use password auth, who administers
the csai.foundation tenant, which PowerDMARC domains report nowhere, 27 unmanaged macOS devices, is
the Cloudflare DNS token valid — and none could be answered without manual archaeology. Security
posture that is expensive to check is checked rarely, and rarely is the same as never on the days it
matters.

**It is an Operations360 input.** The estate CSA runs on is one of the six subject-scoped systems;
this is the Workspace slice of its evidence.

**The classification is reusable regardless of the client.** 709 methods across 26 Workspace APIs,
each marked read-safe, mutating, or read-requiring-write-authority. That analysis holds whether or
not anyone runs this code.

## Why not the alternatives

| Alternative | Why not |
|---|---|
| **Google's own MCP servers** | They cover Gmail and Calendar as an end user. There is no admin or audit surface among them |
| **GAM** | The prior art, and genuinely capable. It is a CLI built for a human operator and grants whatever the admin holds — there is no read-only mode enforced anywhere, and no capability layer an agent can be constrained by |
| **The admin console** | Answers one question at a time, by hand, leaving no artifact. It is why these questions go unasked |
| **A commercial CASB or posture tool** | Buys the reads and the dashboards, and costs per seat. Worth revisiting if the scope grows beyond Workspace; for one tenant and one API surface it is a large purchase to answer questions we can compute |

## The security component is the product, not packaging

Every alternative above answers questions by holding an admin credential with full authority. This
project holds one too — a service account with domain-wide delegation, which can read every mailbox
and every file in the tenant.

The difference is what constrains it:

- **390 mutating methods are absent from the client**, not gated in it. No write path to disable.
- **Read-only is enforced on Google's side**, in a domain-wide-delegation scope allowlist that only a
  Workspace super admin can edit. Google refuses to mint a token for an unlisted scope, so a client
  rewritten to request `gmail.modify` gets nothing back.
- **The scopes are chosen against what they grant, not what they are named.** `gmail.readonly` is
  deferred because it reads every message body in every mailbox, when the actual requirement —
  envelope metadata — needs no Gmail scope at all.

That is the argument for building rather than buying or scripting: **anyone can get the reads. The
work is making the reads safe to hand to an agent.**

## Operational burden

Low and honest. No service, no listener, no deployment, no stored data — a library and a local stdio
server. The recurring costs are re-running the 709-method classification when Google ships, and
reviewing the scope allowlist when someone wants a new read. Both are tracked in `TODO.md`.

## AI enablement

This project exists *because* of AI enablement rather than merely using it: the reason to make the
tenant queryable is that an agent can then ask the follow-up question, and the one after that,
without a human composing each console query. The classification work itself was AI-performed against
Google's Discovery documents, which is what made enumerating 709 methods proportionate at all.
