#!/usr/bin/env bash
set -euo pipefail

cd /workspace/goose-skills

# Idempotency guard
if grep -qF "2. **Search LinkedIn posts** \u2014 Use the `linkedin-post-research` skill (Apify-bas" "skills/capabilities/champion-tracker/SKILL.md" && grep -qF "- `skills/capabilities/linkedin-post-research/scripts/search_posts.py` \u2014 LinkedI" "skills/capabilities/customer-discovery/SKILL.md" && grep -qF "Delegate to the `linkedin-post-research` skill (uses the `apimaestro~linkedin-po" "skills/composites/industry-scanner/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/capabilities/champion-tracker/SKILL.md b/skills/capabilities/champion-tracker/SKILL.md
@@ -26,8 +26,8 @@ Detect when product champions change jobs and qualify their new companies agains
 Build the initial champion list from public sources. This is done by the agent, not the script.
 
 1. **Scrape reviews** — Use `review-site-scraper` skill to pull G2/Trustpilot reviews. Extract reviewer names + companies.
-2. **Search LinkedIn posts** — Use Crustdata MCP to find people who posted about the product.
-3. **Resolve LinkedIn URLs** — Use Crustdata MCP to search by name + company → get profile URLs.
+2. **Search LinkedIn posts** — Use the `linkedin-post-research` skill (Apify-based) to find people who posted about the product.
+3. **Resolve LinkedIn URLs** — Use Fiber `/v1/kitchen-sink/person` (name + company → profile URL) or ContactOut via Orthogonal.
 4. **Compile CSV** — Merge all sources into `champions.csv` with required columns.
 
 ### Phase B: Track Job Changes (script-driven, repeatable)
diff --git a/skills/capabilities/customer-discovery/SKILL.md b/skills/capabilities/customer-discovery/SKILL.md
@@ -255,7 +255,7 @@ All scripts require `requests`: `pip3 install requests`
 
 External skill scripts (use if available):
 - `skills/capabilities/review-site-scraper/scripts/scrape_reviews.py` — G2/Capterra/Trustpilot reviews (requires Apify token)
-- `skills/capabilities/linkedin-post-research/scripts/search_posts.py` — LinkedIn post search (requires Crustdata API key)
+- `skills/capabilities/linkedin-post-research/scripts/search_posts.py` — LinkedIn post search (requires Apify token)
 
 ## Cost
 
diff --git a/skills/composites/industry-scanner/SKILL.md b/skills/composites/industry-scanner/SKILL.md
@@ -102,9 +102,9 @@ Read `skills/twitter-mention-tracker/SKILL.md` for full CLI reference.
 
 Search each configured LinkedIn keyword via the linkedin-post-research skill.
 
-Use `RUBE_SEARCH_TOOLS` to find `CRUSTDATA_SEARCH_LINKED_IN_POSTS_BY_KEYWORD`, then search each keyword with `date_posted: "past-day"` (or `"past-week"` for weekly scans).
+Delegate to the `linkedin-post-research` skill (uses the `apimaestro~linkedin-posts-search-scraper-no-cookies` Apify actor). Search each keyword with `date_posted: "past-day"` (or `"past-week"` for weekly scans).
 
-Read `skills/linkedin-post-research/SKILL.md` for the full Rube/Crustdata workflow.
+Read `skills/linkedin-post-research/SKILL.md` for the full Apify workflow.
 
 #### 2F. Hacker News
 
@@ -365,4 +365,4 @@ No additional dependencies beyond what the sub-skills require:
 - `requests` (Python) — for blog-feed-monitor, reddit-post-finder, twitter-mention-tracker, hn-scraper, review-site-scraper, news-monitor
 - `APIFY_API_TOKEN` env var — for Reddit, Twitter, and review scraping
 - `agentmail` + `python-dotenv` — for newsletter-monitor (if configured)
-- Rube/Crustdata connection — for LinkedIn post search (if configured)
+- `APIFY_API_TOKEN` — LinkedIn post search goes through the `linkedin-post-research` skill (Apify-based)
PATCH

echo "Gold patch applied."
