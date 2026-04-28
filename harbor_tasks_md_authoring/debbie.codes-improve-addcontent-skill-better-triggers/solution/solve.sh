#!/usr/bin/env bash
set -euo pipefail

cd /workspace/debbie.codes

# Idempotency guard
if grep -qF "debbie.codes website. Triggered by phrases like: \"add video\", \"add blog\", \"add b" ".agents/skills/add-content/SKILL.md" && grep -qF "playwright-cli open \"<blog-url>\"" ".agents/skills/add-content/references/blog.md" && grep -qF "First, kill any existing dev server on port 3001:" ".agents/skills/add-content/references/environment.md" && grep -qF "description: Discover how to perform manual testing using Playwright MCP without" ".agents/skills/add-content/references/video.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/add-content/SKILL.md b/.agents/skills/add-content/SKILL.md
@@ -1,11 +1,13 @@
 ---
 name: add-content
 description: >
-  Add new content (videos, podcasts, or blog posts) to the debbie.codes website.
-  Use when the user wants to: (1) Add a YouTube video to content/videos/,
-  (2) Add a podcast episode to content/podcasts/, (3) Add a blog post to content/blog/.
-  Handles browser-based metadata extraction via playwright-cli, file creation with
-  correct frontmatter, dev server verification, and PR creation.
+  Use this skill whenever the user says "add video", "add blog post", "add podcast",
+  or provides a URL to add to the site. Adds videos, podcasts, or blog posts to the
+  debbie.codes website. Triggered by phrases like: "add video", "add blog", "add blog post",
+  "add podcast", "add this video", "add this to the site", or any request with a YouTube,
+  podcast, or blog URL to be added as content. Handles browser-based metadata extraction
+  via playwright-cli, file creation with correct frontmatter, dev server verification,
+  and PR creation.
 ---
 
 # Add Content to debbie.codes
diff --git a/.agents/skills/add-content/references/blog.md b/.agents/skills/add-content/references/blog.md
@@ -5,8 +5,7 @@
 Open the blog post URL with playwright-cli:
 
 ```bash
-BLOG_URL='https://example.com/blog-post'  # replace with the target blog URL
-playwright-cli open -- "$BLOG_URL"
+playwright-cli open "<blog-url>"
 ```
 
 Take a snapshot and read the YAML to extract:
diff --git a/.agents/skills/add-content/references/environment.md b/.agents/skills/add-content/references/environment.md
@@ -71,6 +71,14 @@ git push origin add-<type>/<kebab-case-short-title>
 
 ### Install dependencies and start
 
+First, kill any existing dev server on port 3001:
+
+```bash
+kill $(lsof -ti:3001) 2>/dev/null
+```
+
+Then install and start:
+
 ```bash
 export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && npm install 2>&1 | tail -5
 ```
diff --git a/.agents/skills/add-content/references/video.md b/.agents/skills/add-content/references/video.md
@@ -64,16 +64,16 @@ Check with: `grep -h "^tags:" content/videos/*.md | sed 's/tags: \[//;s/\]//;s/,
 
 ## Example
 
-**File**: `content/videos/supercharged-testing-playwright-mcp.md`
+**File**: `content/videos/manual-testing-with-playwright-mcp-no-code-just-prompts.md`
 
 ```yaml
 ---
-title: "Supercharged Testing: AI-Powered Workflows with Playwright + MCP - Debbie O'Brien"
-date: 2026-02-11
-description: "Learn how to supercharge your end-to-end testing strategy by combining Playwright with the Playwright MCP Server for AI-assisted workflows."
-video: Numb52aJkJw
-tags: [playwright, testing, ai, mcp, conference-talk]
-host: NDC Conferences
-image: https://img.youtube.com/vi/Numb52aJkJw/sddefault.jpg
+title: Manual Testing with Playwright MCP – No Code, Just Prompts!
+date: 2025-07-12
+description: Discover how to perform manual testing using Playwright MCP without writing any code, using simple prompts instead. This revolutionary approach makes testing accessible to everyone, regardless of their coding experience.
+video: 2vnttb-YZrA
+tags: [playwright, mcp, testing, ai]
+host: Debbie's youtube channel
+image: https://img.youtube.com/vi/2vnttb-YZrA/sddefault.jpg
 ---
 ```
PATCH

echo "Gold patch applied."
