#!/usr/bin/env bash
set -euo pipefail

cd /workspace/antigravity-awesome-skills

# Idempotency guard
if grep -qF "description: Professional code review with auto CHANGELOG generation, integrated" "skills/codex-review/SKILL.md" && grep -qF "description: Automatically fetch latest library/framework documentation for Clau" "skills/context7-auto-research/SKILL.md" && grep -qF "description: Semantic search, similar content discovery, and structured research" "skills/exa-search/SKILL.md" && grep -qF "description: Deep web scraping, screenshots, PDF parsing, and website crawling u" "skills/firecrawl-scraper/SKILL.md" && grep -qF "description: Web search, content extraction, crawling, and research capabilities" "skills/tavily-web/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/codex-review/SKILL.md b/skills/codex-review/SKILL.md
@@ -0,0 +1,37 @@
+---
+name: codex-review
+description: Professional code review with auto CHANGELOG generation, integrated with Codex AI
+---
+
+# codex-review
+
+## Overview
+Professional code review with auto CHANGELOG generation, integrated with Codex AI
+
+## When to Use
+- When you want professional code review before commits
+- When you need automatic CHANGELOG generation
+- When reviewing large-scale refactoring
+
+## Installation
+```bash
+npx skills add -g BenedictKing/codex-review
+```
+
+## Step-by-Step Guide
+1. Install the skill using the command above
+2. Ensure Codex CLI is installed
+3. Use `/codex-review` or natural language triggers
+
+## Examples
+See [GitHub Repository](https://github.com/BenedictKing/codex-review) for examples.
+
+## Best Practices
+- Keep CHANGELOG.md in your project root
+- Use conventional commit messages
+
+## Troubleshooting
+See the GitHub repository for troubleshooting guides.
+
+## Related Skills
+- context7-auto-research, tavily-web, exa-search, firecrawl-scraper
diff --git a/skills/context7-auto-research/SKILL.md b/skills/context7-auto-research/SKILL.md
@@ -0,0 +1,36 @@
+---
+name: context7-auto-research
+description: Automatically fetch latest library/framework documentation for Claude Code via Context7 API
+---
+
+# context7-auto-research
+
+## Overview
+Automatically fetch latest library/framework documentation for Claude Code via Context7 API
+
+## When to Use
+- When you need up-to-date documentation for libraries and frameworks
+- When asking about React, Next.js, Prisma, or any other popular library
+
+## Installation
+```bash
+npx skills add -g BenedictKing/context7-auto-research
+```
+
+## Step-by-Step Guide
+1. Install the skill using the command above
+2. Configure API key (optional, see GitHub repo for details)
+3. Use naturally in Claude Code conversations
+
+## Examples
+See [GitHub Repository](https://github.com/BenedictKing/context7-auto-research) for examples.
+
+## Best Practices
+- Configure API keys via environment variables for higher rate limits
+- Use the skill's auto-trigger feature for seamless integration
+
+## Troubleshooting
+See the GitHub repository for troubleshooting guides.
+
+## Related Skills
+- tavily-web, exa-search, firecrawl-scraper, codex-review
diff --git a/skills/exa-search/SKILL.md b/skills/exa-search/SKILL.md
@@ -0,0 +1,36 @@
+---
+name: exa-search
+description: Semantic search, similar content discovery, and structured research using Exa API
+---
+
+# exa-search
+
+## Overview
+Semantic search, similar content discovery, and structured research using Exa API
+
+## When to Use
+- When you need semantic/embeddings-based search
+- When finding similar content
+- When searching by category (company, people, research papers, etc.)
+
+## Installation
+```bash
+npx skills add -g BenedictKing/exa-search
+```
+
+## Step-by-Step Guide
+1. Install the skill using the command above
+2. Configure Exa API key
+3. Use naturally in Claude Code conversations
+
+## Examples
+See [GitHub Repository](https://github.com/BenedictKing/exa-search) for examples.
+
+## Best Practices
+- Configure API keys via environment variables
+
+## Troubleshooting
+See the GitHub repository for troubleshooting guides.
+
+## Related Skills
+- context7-auto-research, tavily-web, firecrawl-scraper, codex-review
diff --git a/skills/firecrawl-scraper/SKILL.md b/skills/firecrawl-scraper/SKILL.md
@@ -0,0 +1,37 @@
+---
+name: firecrawl-scraper
+description: Deep web scraping, screenshots, PDF parsing, and website crawling using Firecrawl API
+---
+
+# firecrawl-scraper
+
+## Overview
+Deep web scraping, screenshots, PDF parsing, and website crawling using Firecrawl API
+
+## When to Use
+- When you need deep content extraction from web pages
+- When page interaction is required (clicking, scrolling, etc.)
+- When you want screenshots or PDF parsing
+- When batch scraping multiple URLs
+
+## Installation
+```bash
+npx skills add -g BenedictKing/firecrawl-scraper
+```
+
+## Step-by-Step Guide
+1. Install the skill using the command above
+2. Configure Firecrawl API key
+3. Use naturally in Claude Code conversations
+
+## Examples
+See [GitHub Repository](https://github.com/BenedictKing/firecrawl-scraper) for examples.
+
+## Best Practices
+- Configure API keys via environment variables
+
+## Troubleshooting
+See the GitHub repository for troubleshooting guides.
+
+## Related Skills
+- context7-auto-research, tavily-web, exa-search, codex-review
diff --git a/skills/tavily-web/SKILL.md b/skills/tavily-web/SKILL.md
@@ -0,0 +1,36 @@
+---
+name: tavily-web
+description: Web search, content extraction, crawling, and research capabilities using Tavily API
+---
+
+# tavily-web
+
+## Overview
+Web search, content extraction, crawling, and research capabilities using Tavily API
+
+## When to Use
+- When you need to search the web for current information
+- When extracting content from URLs
+- When crawling websites
+
+## Installation
+```bash
+npx skills add -g BenedictKing/tavily-web
+```
+
+## Step-by-Step Guide
+1. Install the skill using the command above
+2. Configure Tavily API key
+3. Use naturally in Claude Code conversations
+
+## Examples
+See [GitHub Repository](https://github.com/BenedictKing/tavily-web) for examples.
+
+## Best Practices
+- Configure API keys via environment variables
+
+## Troubleshooting
+See the GitHub repository for troubleshooting guides.
+
+## Related Skills
+- context7-auto-research, exa-search, firecrawl-scraper, codex-review
PATCH

echo "Gold patch applied."
