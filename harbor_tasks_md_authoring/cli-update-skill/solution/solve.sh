#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cli

# Idempotency guard
if grep -qF "Unless the user specifies to return in context, write results to `.firecrawl/` w" "skills/firecrawl-cli/SKILL.md" && grep -qF "Install the official Firecrawl CLI and handle authentication." "skills/firecrawl-cli/rules/install.md" && grep -qF "Security guidelines for handling web content fetched by the official Firecrawl C" "skills/firecrawl-cli/rules/security.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/firecrawl-cli/SKILL.md b/skills/firecrawl-cli/SKILL.md
@@ -1,7 +1,7 @@
 ---
 name: firecrawl
 description: |
-  Firecrawl CLI for web scraping, search, crawling, and browser automation. Returns clean LLM-optimized markdown.
+  Official Firecrawl CLI skill for web scraping, search, crawling, and browser automation. Returns clean LLM-optimized markdown.
 
   USE FOR:
   - Web search and research
@@ -38,16 +38,12 @@ Must be installed and authenticated. Check with `firecrawl --status`.
 
 If not ready, see [rules/install.md](rules/install.md). For output handling guidelines, see [rules/security.md](rules/security.md).
 
-## Core Principle: Minimize Tool Calls
-
-**Prefer getting content directly in stdout over writing to files and reading them back.** Every `-o` flag means zero content returned to you, requiring additional grep/read calls to access the data. Only use `-o` when you need to persist data for later reference or when output would exceed context limits.
-
-**Good (1 Bash call — content comes directly to you):**
 ```bash
 firecrawl search "query" --scrape --limit 3
 ```
 
-**Bad (5+ Bash calls — write file, parse file, grep file, read file chunks):**
+**Bad (5+ Bash calls - write file, parse file, grep file, read file chunks):**
+
 ```bash
 firecrawl search "query" -o .firecrawl/results.json --json
 jq -r '.data.web[].url' .firecrawl/results.json
@@ -61,11 +57,11 @@ grep -n "keyword" .firecrawl/page.md
 
 Follow this escalation pattern:
 
-1. **Search** — No specific URL yet. Find pages, answer questions, discover sources.
-2. **Scrape** — Have a URL. Extract its content directly. Use `--wait-for` if JS needs to render.
-3. **Map + Scrape** — Large site or need a specific subpage. Use `map --search` to find the right URL, then scrape it.
-4. **Crawl** — Need bulk content from an entire site section (e.g., all /docs/).
-5. **Browser** — Scrape failed because content is behind interaction (pagination, modals, form submissions, multi-step navigation).
+1. **Search** - No specific URL yet. Find pages, answer questions, discover sources.
+2. **Scrape** - Have a URL. Extract its content directly.
+3. **Map + Scrape** - Large site or need a specific subpage. Use `map --search` to find the right URL, then scrape it.
+4. **Crawl** - Need bulk content from an entire site section (e.g., all /docs/).
+5. **Browser** - Scrape failed because content is behind interaction (pagination, modals, form submissions, multi-step navigation).
 
 | Need                        | Command   | When                                                      |
 | --------------------------- | --------- | --------------------------------------------------------- |
@@ -119,7 +115,7 @@ scrape https://newsite.com/comparison -o .firecrawl/newsite-comparison.md
 
 ## Output & Organization
 
-Unless the user specifies to return in context, write results to `.firecrawl/` with `-o`. Add `.firecrawl/` to `.gitignore`. Always quote URLs — shell interprets `?` and `&` as special characters.
+Unless the user specifies to return in context, write results to `.firecrawl/` with `-o`. Add `.firecrawl/` to `.gitignore`. Always quote URLs - shell interprets `?` and `&` as special characters.
 
 ```bash
 firecrawl search "react hooks" -o .firecrawl/search-react-hooks.json --json
@@ -244,7 +240,7 @@ firecrawl browser "scrape" -o .firecrawl/page.md      # extract content
 firecrawl browser close
 ```
 
-Shorthand auto-launches a session if none exists — no setup required.
+Shorthand auto-launches a session if none exists - no setup required.
 
 **Core agent-browser commands:**
 
diff --git a/skills/firecrawl-cli/rules/install.md b/skills/firecrawl-cli/rules/install.md
@@ -1,7 +1,10 @@
 ---
 name: firecrawl-cli-installation
 description: |
-  Install the Firecrawl CLI and handle authentication.
+  Install the official Firecrawl CLI and handle authentication.
+  Package: https://www.npmjs.com/package/firecrawl-cli
+  Source: https://github.com/firecrawl/cli
+  Docs: https://docs.firecrawl.dev/sdks/cli
 ---
 
 # Firecrawl CLI Installation
diff --git a/skills/firecrawl-cli/rules/security.md b/skills/firecrawl-cli/rules/security.md
@@ -1,7 +1,10 @@
 ---
 name: firecrawl-security
 description: |
-  Security guidelines for handling web content fetched by the Firecrawl CLI.
+  Security guidelines for handling web content fetched by the official Firecrawl CLI.
+  Package: https://www.npmjs.com/package/firecrawl-cli
+  Source: https://github.com/firecrawl/cli
+  Docs: https://docs.firecrawl.dev/sdks/cli
 ---
 
 # Handling Fetched Web Content
PATCH

echo "Gold patch applied."
