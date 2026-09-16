# Provenance of the Discovery snapshots

Fetched **2026-09-16** by `scripts/fetch_specs.sh`, refreshing the 2026-09-01 set. Every file
below carries its fetch source, upstream `revision`, raw sha256, canonical sha256 and byte count,
in the format [`csa-google-gmail-calendar`](https://github.com/CloudSecurityAlliance/csa-google-gmail-calendar)
established. The same fields are emitted machine-readably to `analysis/provenance.csv` by
`scripts/inventory.py`.

Google publishes **Discovery documents**, not OpenAPI. They are the artifact Google's own client
libraries are generated from, so they are authoritative rather than best-effort — but they are
snapshots of a moving target. **Re-fetch and diff before trusting them.**

Each method's `scopes` array is the only source used for scope claims in this repository.
Google's prose documentation is known to disagree with it: `csa-google-gmail-calendar` found the
Calendar docs listing three read-only scopes on the page describing event creation, and the Gmail
docs omitting `gmail.modify` while describing trash.

## The snapshots

| file | id | revision | source URL | sha256 | canonical sha256 | bytes |
|---|---|---|---|---|---|---|
| `admin-datatransfer_v1.json` | `admin:datatransfer_v1` | 20260913 | https://admin.googleapis.com/$discovery/rest?version=datatransfer_v1 | `78da0010808c0a96…` | `fcd0dc354b80b5d5…` | 15933 |
| `admin-directory_v1.json` | `admin:directory_v1` | 20260913 | https://admin.googleapis.com/$discovery/rest?version=directory_v1 | `fd64bd5cd1220d9b…` | `13d55dfb9b9e229d…` | 386772 |
| `admin-reports_v1.json` | `admin:reports_v1` | 20260913 | https://admin.googleapis.com/$discovery/rest?version=reports_v1 | `b2d69328aa03a0a0…` | `ad80f7c37c95be3c…` | 94956 |
| `alertcenter-v1beta1.json` | `alertcenter:v1beta1` | 20260914 | https://alertcenter.googleapis.com/$discovery/rest?version=v1beta1 | `080be751b1682e2a…` | `af6572db5a0602fa…` | 99710 |
| `calendar-v3.json` | `calendar:v3` | 20260826 | https://calendar-json.googleapis.com/$discovery/rest?version=v3 | `e1ccc2b94a3178b6…` | `3bdf9518a62f3479…` | 169810 |
| `chromemanagement-v1.json` | `chromemanagement:v1` | 20260915 | https://chromemanagement.googleapis.com/$discovery/rest?version=v1 | `9083efdedd1c2c7a…` | `092d3ec7eb49e5b9…` | 393366 |
| `chromepolicy-v1.json` | `chromepolicy:v1` | 20260915 | https://chromepolicy.googleapis.com/$discovery/rest?version=v1 | `22a69137d956b2a9…` | `cada14e3bb1ce789…` | 81855 |
| `cloudidentity-v1.json` | `cloudidentity:v1` | 20260914 | https://cloudidentity.googleapis.com/$discovery/rest?version=v1 | `21be5e7134602982…` | `bf3b3cf616a6feca…` | 236728 |
| `cloudsearch-v1.json` | `cloudsearch:v1` | 20260819 | https://cloudsearch.googleapis.com/$discovery/rest?version=v1 | `89e6651feab8c986…` | `1e8dbbaf9fb138f1…` | 332906 |
| `docs-v1.json` | `docs:v1` | 20260909 | https://docs.googleapis.com/$discovery/rest?version=v1 | `f5fabc3607d5d638…` | `3651bef78b376a51…` | 236937 |
| `drive-v3.json` | `drive:v3` | 20260904 | https://www.googleapis.com/discovery/v1/apis/drive/v3/rest | `37fe86fda0c1f580…` | `f943300a8208b927…` | 269466 |
| `driveactivity-v2.json` | `driveactivity:v2` | 20260913 | https://driveactivity.googleapis.com/$discovery/rest?version=v2 | `73f3d11e76cdf934…` | `3cdbb2fb82027436…` | 48869 |
| `forms-v1.json` | `forms:v1` | 20260909 | https://forms.googleapis.com/$discovery/rest?version=v1 | `3c8cb62fac7989e0…` | `cf833f1720b5d7b9…` | 69010 |
| `gmail-v1.json` | `gmail:v1` | 20260907 | https://gmail.googleapis.com/$discovery/rest?version=v1 | `67d12d2b318b0ff6…` | `ff15bf5eecd7ae66…` | 217687 |
| `gmailpostmastertools-v2.json` | `gmailpostmastertools:v2` | 20260915 | https://gmailpostmastertools.googleapis.com/$discovery/rest?version=v2 | `79b2fa94e76bd511…` | `85ccb1e1388b7223…` | 54505 |
| `groupssettings-v1.json` | `groupssettings:v1` | 20220614 | https://groupssettings.googleapis.com/$discovery/rest?version=v1 | `9ef2d75cf6bb83f0…` | `c40c5ba51914961e…` | 28402 |
| `keep-v1.json` | `keep:v1` | 20260906 | https://keep.googleapis.com/$discovery/rest?version=v1 | `65d40cc965faedaa…` | `cd79d9af6835c642…` | 22366 |
| `licensing-v1.json` | `licensing:v1` | 20260914 | https://licensing.googleapis.com/$discovery/rest?version=v1 | `261d0ff44660cdf3…` | `35074f3bea4ab85b…` | 20725 |
| `meet-v2.json` | `meet:v2` | 20260914 | https://meet.googleapis.com/$discovery/rest?version=v2 | `83947503c342184d…` | `960edba8f080db51…` | 78342 |
| `people-v1.json` | `people:v1` | 20260914 | https://people.googleapis.com/$discovery/rest?version=v1 | `cbfdbafcee602b67…` | `452e85a50db2876d…` | 144907 |
| `script-v1.json` | `script:v1` | 20260906 | https://script.googleapis.com/$discovery/rest?version=v1 | `f3e0d95798e5eca7…` | `8e0deef14001ee6d…` | 66588 |
| `sheets-v4.json` | `sheets:v4` | 20260909 | https://sheets.googleapis.com/$discovery/rest?version=v4 | `9933a356892fc661…` | `d54285a6ed7c70e1…` | 378032 |
| `slides-v1.json` | `slides:v1` | 20260909 | https://slides.googleapis.com/$discovery/rest?version=v1 | `e3d2d91ca6b8bf0e…` | `a2c694da9720274f…` | 227920 |
| `tasks-v1.json` | `tasks:v1` | 20260915 | https://tasks.googleapis.com/$discovery/rest?version=v1 | `d503782e3a3f87d4…` | `324d79a49a525508…` | 31887 |
| `vault-v1.json` | `vault:v1` | 20260905 | https://vault.googleapis.com/$discovery/rest?version=v1 | `3a9684370c293cf3…` | `eeff588afaf412e5…` | 110660 |
| `workspaceevents-v1.json` | `workspaceevents:v1` | 20260906 | https://workspaceevents.googleapis.com/$discovery/rest?version=v1 | `ec6b63b33cbc6900…` | `59b6549c9412f05d…` | 77739 |

Full digests (raw sha256, of the exact bytes committed here):

```
78da0010808c0a96c19115ca21a65d8fb29d180a1474c1f6ba18917b89aa6496  admin-datatransfer_v1.json
fd64bd5cd1220d9be2885cbe8d0fa7580486dd81294f4bef7632980e50a19b7e  admin-directory_v1.json
b2d69328aa03a0a05edda6e31ef0ab811f3f08633714c0a0be732b5609ffda47  admin-reports_v1.json
080be751b1682e2a802ae3504ac0af724686c78c5b24eb377ec9a80ecb98dcb4  alertcenter-v1beta1.json
e1ccc2b94a3178b6e00cf1a7051fb9e352647b6000b8509f11881ef1bc8e33ac  calendar-v3.json
9083efdedd1c2c7a99522ea0630dca73fd6d2449d814cbbd849337da73c95fc4  chromemanagement-v1.json
22a69137d956b2a9daba677cf1efcf8cb920cb2a1b286946060500ea16466dc6  chromepolicy-v1.json
21be5e7134602982122cfe0759bfb19eb23ce49d8697ebba768f1cb88b2fcc81  cloudidentity-v1.json
89e6651feab8c986d4f267a2339dc1b6adabb52d3b8ac5cedb56d5b9d50204ac  cloudsearch-v1.json
f5fabc3607d5d6382c5544a6ed074f89f1118a332929fee137f06af98ecb679b  docs-v1.json
37fe86fda0c1f58072e1e6e9f46f2d8e8692073d767d7492aeaca2c83b4bb1d8  drive-v3.json
73f3d11e76cdf934691353217d4c78677a5dc8a4692ffe362315152347c8a1ec  driveactivity-v2.json
3c8cb62fac7989e095a648d6b93ca3ab11966bea1562d526741213a3fa25f6a6  forms-v1.json
67d12d2b318b0ff648e001b5ba93c3f552551cd79c1209f4a651d69f13c7cd33  gmail-v1.json
79b2fa94e76bd511a08427508107101cfc32b621dc45744f35d2057e266c37be  gmailpostmastertools-v2.json
9ef2d75cf6bb83f068370c1cfeb8d72b4bf0eeea4f45aef4298d5215afddb2c8  groupssettings-v1.json
65d40cc965faedaadd15e41c86f9bd3e476b3fe48827df5faa61fb9fcb4780cc  keep-v1.json
261d0ff44660cdf31ac01b774f24898663e3d98d193da9f1dcc402c897dfe890  licensing-v1.json
83947503c342184d1953b1909dddc70bdf01fbc69e7331bd97983561bd59aa2e  meet-v2.json
cbfdbafcee602b6740769d909a10bfe6048b96e7ba2a3d052938d8bf9101cffc  people-v1.json
f3e0d95798e5eca74950076ab5aa91a822acb1b877d03eece2101b934cbf3218  script-v1.json
9933a356892fc6613fb6f2177ef631b736575f1fbf85bc90cbb8301d23f92b63  sheets-v4.json
e3d2d91ca6b8bf0ed4190bcf52ea2614e56d8a90f5a8e33e1a514571437645b3  slides-v1.json
d503782e3a3f87d4132fbc9684545f6ebcc9a2df3505effd64092712bd157a95  tasks-v1.json
3a9684370c293cf394819ee8cfef9843d986f8c06a83371de49a48e281240c6b  vault-v1.json
ec6b63b33cbc6900a42d21867bc8c338ade2644b023755bc546f07a2836d1ab6  workspaceevents-v1.json
```

## Why there are two digests

**The raw sha256 is not a drift signal.** Google's Discovery service serializes JSON object keys
in a non-deterministic order, so two fetches of an identical document produce different bytes and
a different sha256. On the 2026-09-16 re-fetch, **all 26 files came back with a different raw
sha256 — but three of them were semantically identical to the stored copy**: `calendar-v3`,
`cloudsearch-v1` and `groupssettings-v1`, each with the same revision, the same byte count, and
only the key order reshuffled. Comparing raw digests alone would have reported drift in 26 of 26
files where the true answer was 23.

The **canonical sha256** is the digest of the document re-serialized with sorted keys and no
insignificant whitespace. It is stable across fetches and is the digest to compare when answering
"has this changed":

```bash
python3 -c "import json,hashlib,sys;print(hashlib.sha256(json.dumps(json.load(open(sys.argv[1])),sort_keys=True,separators=(',',':')).encode()).hexdigest())" specs/gmail-v1.json
```

The raw sha256 stays recorded because it identifies the exact bytes committed here.

Following the sibling repo's precedent, the three semantically-identical documents were **not**
re-committed — churning 580 KB of bytes to record a key reshuffle would make every future diff
harder to read for no information gained. Their entries below are the 2026-09-01 bytes, re-verified
as current on 2026-09-16.

## Revision ages, oldest first

`groupssettings:v1` is revision **20220614** — over four years old, and the only snapshot here not
revised within the last three weeks. It is also one of the four APIs with no read-only scope. An
API Google has not touched since 2022 is unlikely to grow one.

`cloudsearch:v1` (20260819) and `calendar:v3` (20260826) are next oldest and were unchanged on
re-fetch. Everything else carries a 2026-09 revision.

## Change log

- **2026-09-16** — Re-fetched all 26. **23 revisions moved**; 3 were unchanged. **9 methods were
  added, 0 removed, and no existing method's `scopes` array changed** — the read/write
  classification of every previously-classified method is intact. The new methods are 3
  Chrome Management SaaS-usage reports (all `chrome.management.reports.readonly`) and 6
  `meet.spaces.members.*` (2 reads under `meetings.space.readonly`, 4 mutating). Totals moved
  709 → 718 methods, 255 → 260 `READ_SAFE`, 390 → 394 `MUTATING`; `READ_NEEDS_RW` (52),
  `READ_NO_SCOPE` (12), the scope catalogue (175) and the **phase-1 allowlist (34 scopes) were
  all unchanged**. Added the canonical digest, and the per-file source URL and byte count this
  file had previously delegated to `analysis/provenance.csv`.
- **2026-09-01** — Initial fetch of all 26 documents.
