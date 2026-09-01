#!/usr/bin/env bash
# Fetch the upstream Google Discovery documents this repo reasons about.
# Re-run to refresh; `scripts/inventory.py` derives everything else from specs/.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p specs

fetch() {  # fetch <local-name> <url>
  curl -sS --max-time 90 --fail-with-body "$2" -o "specs/$1" \
    && printf '  %-38s %8s bytes\n' "$1" "$(wc -c < "specs/$1" | tr -d ' ')" \
    || printf '  %-38s FAILED\n' "$1"
}

D='https://%s.googleapis.com/$discovery/rest?version=%s'

fetch admin-directory_v1.json   "$(printf "$D" admin directory_v1)"
fetch admin-reports_v1.json     "$(printf "$D" admin reports_v1)"
fetch admin-datatransfer_v1.json "$(printf "$D" admin datatransfer_v1)"
fetch groupssettings-v1.json    "$(printf "$D" groupssettings v1)"
fetch cloudidentity-v1.json     "$(printf "$D" cloudidentity v1)"
fetch alertcenter-v1beta1.json  "$(printf "$D" alertcenter v1beta1)"
fetch vault-v1.json             "$(printf "$D" vault v1)"
fetch driveactivity-v2.json     "$(printf "$D" driveactivity v2)"
fetch gmail-v1.json             "$(printf "$D" gmail v1)"
fetch licensing-v1.json         "$(printf "$D" licensing v1)"
fetch chromemanagement-v1.json  "$(printf "$D" chromemanagement v1)"
fetch chromepolicy-v1.json      "$(printf "$D" chromepolicy v1)"
fetch meet-v2.json              "$(printf "$D" meet v2)"
fetch keep-v1.json              "$(printf "$D" keep v1)"
fetch gmailpostmastertools-v2.json "$(printf "$D" gmailpostmastertools v2)"
fetch workspaceevents-v1.json   "$(printf "$D" workspaceevents v1)"
fetch cloudsearch-v1.json       "$(printf "$D" cloudsearch v1)"
fetch script-v1.json            "$(printf "$D" script v1)"
fetch tasks-v1.json             "$(printf "$D" tasks v1)"
fetch forms-v1.json             "$(printf "$D" forms v1)"
fetch people-v1.json            "$(printf "$D" people v1)"
# Not on the *.googleapis.com discovery host:
fetch calendar-v3.json 'https://calendar-json.googleapis.com/$discovery/rest?version=v3'
fetch drive-v3.json    'https://www.googleapis.com/discovery/v1/apis/drive/v3/rest'
fetch docs-v1.json     'https://docs.googleapis.com/$discovery/rest?version=v1'
fetch sheets-v4.json   'https://sheets.googleapis.com/$discovery/rest?version=v4'
fetch slides-v1.json   'https://slides.googleapis.com/$discovery/rest?version=v1'
