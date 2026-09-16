# Does Google already ship this? — the official-MCP-server question

**Answer, as probed on 2026-09-16: no. Google runs eight first-party MCP servers on
`*.googleapis.com/mcp/v1`, and not one of them touches the Workspace admin surface.**

This matters because it is the build/buy question for the whole repository. If Google shipped an
official MCP server for the Admin SDK, most of this project would be redundant. It has been an
assumption until now; this file makes it an evidenced claim with a date on it, so the next person
re-runs the probe rather than re-deciding from memory.

## Method

Unauthenticated JSON-RPC `initialize` POST to `https://<host>.googleapis.com/mcp/v1`:

```bash
curl -sS -X POST -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"probe","version":"1"}}}' \
  https://drivemcp.googleapis.com/mcp/v1
```

A server that exists answers with a JSON-RPC result — `{"result":{"serverInfo":{"name":"StatelessServer","version":"ESF"},...}}`.
A host that does not exist returns Google's generic `Error 404 (Not Found)!!1` HTML page.
`tools/list` also answers unauthenticated, so the tool inventory below needed no credential.

**Control:** `zzzznotarealservicemcp.googleapis.com` returned the same 404 HTML as every negative
result, confirming that a 404 here means absent rather than blocked.

## Result — 8 found, 23 absent

| Host | Result | Tools |
|---|---|---|
| `drivemcp` | **200** | 8 — `copy_file`, `create_file`, `download_file_content`, `get_file_metadata`, `get_file_permissions`, `list_recent_files`, `read_file_content`, `search_files` |
| `gmailmcp` | **200** | 23 — drafts, threads, messages, labels, trash, spam |
| `calendarmcp` | **200** | 9 — `list_events`, `get_event`, `list_calendars`, `suggest_time`, `create_event`, `update_event`, `delete_event`, `respond_to_event`, `search_events` |
| `sheetsmcp` | **200** | 6 — `get_values`, `get_spreadsheet`, `update_spreadsheet`, `update_values`, `update_formulas`, `insert_dimension` |
| `chatmcp` | **200** | 4 — `list_messages`, `search_messages`, `search_conversations`, `send_message` |
| `docsmcp` | **200** | 2 — `read_doc`, `update_doc` |
| `slidesmcp` | **200** | 2 — `read_presentation`, `update_presentation` |
| `workspacemcp` | **200** | 1 — `search_corpus` |
| `adminmcp` · `reportsmcp` · `directorymcp` | **404** | — |
| `admindirectorymcp` · `adminreportsmcp` · `adminsdkmcp` | **404** | — |
| `workspaceadminmcp` · `directoryadminmcp` · `cloudidentityadminmcp` | **404** | — |
| `auditmcp` · `usersmcp` · `groupsmcp` · `reportingmcp` | **404** | — |
| `vaultmcp` · `alertcentermcp` · `cloudidentitymcp` · `chromemanagementmcp` | **404** | — |
| `keepmcp` · `tasksmcp` · `formsmcp` · `meetmcp` · `peoplemcp` | **404** | — |
| `zzzznotarealservicemcp` *(control)* | **404** | — |

## What it means

**Every one of the eight is an end-user product surface, not an administrative one.** They operate
on *your* files, *your* mail, *your* calendar — the user-credential model this repository's four
predecessors use. There is no `users.list`, no `roleAssignments.list`, no `activities.list`, no
tokens or ASPs or 2SV state, nothing from Vault or Alert Center, and nothing that reads the tenant
rather than an account in it.

`workspacemcp` is the one worth naming explicitly, because the hostname sounds like the whole
suite. It exposes a single tool, `search_corpus`. It is not an admin server.

**Two corrections to what we assumed going in.** We believed the set was Drive, Docs, Sheets and
Slides. Gmail, Calendar, Chat and `workspacemcp` are also live — so the user-facing surface is
twice what we thought, and the overlap with `csa-google-gmail-calendar` and `csa-google-workspace`
is real and worth a look in those repos. Neither changes the conclusion here: the admin surface is
uncovered.

**So the gap this repository fills is intact**, and it is specifically the domain-wide-delegation,
service-account, read-the-whole-tenant shape that Google has not shipped and — given that every
server above is built around an end user's own credential — may not intend to.

## Re-running this

The probe is cheap and needs no credential. Re-run it when the build/buy question comes up again,
and append a dated row rather than editing this one. Google shipping `adminmcp` would be the single
most consequential piece of news this repository could receive.
