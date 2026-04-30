#!/usr/bin/env bash
set -euo pipefail

cd /workspace/marketingskills

# Idempotency guard
if grep -qF "> **Note on schema detection:** `web_fetch` strips `<script>` tags (including JS" "skills/seo-audit/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/seo-audit/SKILL.md b/skills/seo-audit/SKILL.md
@@ -34,6 +34,19 @@ Before auditing, understand:
 
 ## Audit Framework
 
+### ⚠️ Important: Schema Markup Detection Limitation
+
+**`web_fetch` and `curl` cannot reliably detect structured data / schema markup.**
+
+Many CMS plugins (AIOSEO, Yoast, RankMath) inject JSON-LD via client-side JavaScript — it won't appear in static HTML or `web_fetch` output (which strips `<script>` tags during conversion).
+
+**To accurately check for schema markup, use one of these methods:**
+1. **Browser tool** — render the page and run: `document.querySelectorAll('script[type="application/ld+json"]')`
+2. **Google Rich Results Test** — https://search.google.com/test/rich-results
+3. **Screaming Frog export** — if the client provides one, use it (SF renders JavaScript)
+
+**Never report "no schema found" based solely on `web_fetch` or `curl`.** This has led to false audit findings in production.
+
 ### Priority Order
 1. **Crawlability & Indexation** (can Google find and index it?)
 2. **Technical Foundations** (is the site fast and functional?)
@@ -364,10 +377,12 @@ Same format as above
 - Google Search Console (essential)
 - Google PageSpeed Insights
 - Bing Webmaster Tools
-- Rich Results Test
+- Rich Results Test (**use this for schema validation — it renders JavaScript**)
 - Mobile-Friendly Test
 - Schema Validator
 
+> **Note on schema detection:** `web_fetch` strips `<script>` tags (including JSON-LD) and cannot detect JS-injected schema. Always use the browser tool, Rich Results Test, or Screaming Frog for schema checks. See the warning at the top of the Audit Framework section.
+
 **Paid Tools** (if available)
 - Screaming Frog
 - Ahrefs / Semrush
PATCH

echo "Gold patch applied."
