#!/usr/bin/env bash
# Dump the publisher pages whose rules the note is shaped by, into sources/venue/.
# The pages themselves are not committed (they are not ours to redistribute); what is
# committed is each page's URL, the HTTP status we got and its SHA-256, so that
# scripts/w_venue.py can re-check every quotation against a fresh dump.
#
# sciencedirect.com answers 403 with a captcha to non-browser clients; the 403 is
# recorded rather than worked around, and everything that would have come from it is
# marked unverified in results/json/w_venue.json.
set -euo pipefail
cd "$(dirname "$0")/.."
DIR=sources/venue
mkdir -p "$DIR"
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'

fetch() {   # fetch <name> <url>
    local name=$1 url=$2 code
    code=$(curl -sL --max-time 60 -A "$UA" -o "$DIR/$name.html" -w "%{http_code}" "$url" || echo 000)
    printf '%s\n' "$url" > "$DIR/$name.url"
    printf '%s\n' "$code" > "$DIR/$name.http"
    echo "$code  $name"
}

fetch ipl_journal_page                 "https://shop.elsevier.com/journals/information-processing-letters/0020-0190"
fetch elsevier_generative_ai_policy    "https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals"
fetch elsevier_pricing_policy          "https://www.elsevier.com/about/policies-and-standards/pricing"
fetch ipl_guide_for_authors_blocked    "https://www.sciencedirect.com/journal/information-processing-letters/publish/guide-for-authors"
# The live guide is unreachable from here, so the last readable copy is taken from the Internet
# Archive. It is a 2024-04-24 snapshot -- older than the note, and treated as dated evidence:
# every rule quoted from it is marked as such in results/json/w_venue.json and has to be
# confirmed against the live page in a browser before submission.
fetch ipl_guide_for_authors_wayback2024 "http://web.archive.org/web/20240424192433/https://www.sciencedirect.com/journal/information-processing-letters/publish/guide-for-authors"

(cd "$DIR" && sha256sum *.html > SHA256)
