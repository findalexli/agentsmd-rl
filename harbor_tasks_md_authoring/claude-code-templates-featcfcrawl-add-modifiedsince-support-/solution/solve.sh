#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-code-templates

# Idempotency guard
if grep -qF "Only crawls pages modified since the given date. Skipped pages appear with `stat" "cli-tool/components/skills/utilities/cf-crawl/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/cli-tool/components/skills/utilities/cf-crawl/SKILL.md b/cli-tool/components/skills/utilities/cf-crawl/SKILL.md
@@ -69,6 +69,22 @@ curl -s -X POST "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCO
   }'
 ```
 
+For incremental crawls, add the `modifiedSince` parameter (Unix timestamp in seconds):
+
+```bash
+curl -s -X POST "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/browser-rendering/crawl" \
+  -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
+  -H "Content-Type: application/json" \
+  -d '{
+    "url": "<TARGET_URL>",
+    "limit": <NUMBER_OF_PAGES>,
+    "formats": ["markdown"],
+    "modifiedSince": <UNIX_TIMESTAMP>
+  }'
+```
+
+When `--since` is provided, convert to Unix timestamp: `date -d "2026-03-10" +%s` (Linux) or `date -j -f "%Y-%m-%d" "2026-03-10" +%s` (macOS).
+
 The response returns a job ID:
 ```json
 {"success": true, "result": "job-uuid-here"}
@@ -92,6 +108,14 @@ Possible job statuses:
 
 ### Step 5: Retrieve Results
 
+When using `modifiedSince`, check for skipped pages to see what was unchanged:
+
+```bash
+# See which pages were skipped (not modified since the given timestamp)
+curl -s -X GET "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/browser-rendering/crawl/<JOB_ID>?status=skipped&limit=50" \
+  -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}"
+```
+
 Fetch all completed records using pagination (cursor-based):
 
 ```bash
@@ -177,6 +201,7 @@ print(f'Saved {total_saved} pages to {outdir}/')
 | `render` | boolean | true | `true` = headless browser, `false` = fast HTML fetch |
 | `source` | string | "all" | Page discovery: `all`, `sitemaps`, `links` |
 | `maxAge` | number | 86400 | Cache validity in seconds (max 604800) |
+| `modifiedSince` | number | - | Unix timestamp; only crawl pages modified after this time |
 
 ### Options Object
 
@@ -211,6 +236,12 @@ Crawls up to 50 pages, saves as markdown.
 /cf-crawl https://docs.example.com --limit 100 --include "/guides/**,/api/**" --exclude "/changelog/**"
 ```
 
+### Incremental crawl (diff detection)
+```
+/cf-crawl https://docs.example.com --limit 50 --since 2026-03-10
+```
+Only crawls pages modified since the given date. Skipped pages appear with `status=skipped` in results. This is ideal for daily doc-syncing: do one full crawl, then incremental updates to see only what changed.
+
 ### Fast crawl without JavaScript rendering
 ```
 /cf-crawl https://docs.example.com --no-render --limit 200
@@ -236,6 +267,7 @@ When invoked as `/cf-crawl`, parse the arguments as follows:
 - `--merge`: combine all output into a single file
 - `--output DIR` or `-o DIR`: output directory (default: `.crawl-output`)
 - `--source sitemaps|links|all`: page discovery method (default: all)
+- `--since DATE`: only crawl pages modified since DATE (ISO date like `2026-03-10` or Unix timestamp). Converts to Unix timestamp for the `modifiedSince` API parameter
 
 If no URL is provided, ask the user for the target URL.
 
PATCH

echo "Gold patch applied."
