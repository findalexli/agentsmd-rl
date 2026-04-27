#!/usr/bin/env bash
set -euo pipefail

cd /workspace/baoyu-skills

# Idempotency guard
if grep -qF "Claude Code marketplace plugin providing AI-powered content generation skills. C" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -4,11 +4,11 @@ This file provides guidance to Claude Code (claude.ai/code) when working with co
 
 ## Project Overview
 
-Claude Code marketplace plugin providing AI-powered content generation skills. Skills use Gemini Web API (reverse-engineered) for text/image generation and Chrome CDP for browser automation.
+Claude Code marketplace plugin providing AI-powered content generation skills. Current version: **1.59.0**. Skills use official AI APIs (OpenAI, Google, DashScope, Replicate) or the reverse-engineered Gemini Web API for text/image generation, and Chrome CDP for browser automation.
 
 ## Architecture
 
-Skills are organized into three plugin categories in `marketplace.json`:
+Skills are organized into three plugin categories in `.claude-plugin/marketplace.json`:
 
 ```
 skills/
@@ -19,16 +19,27 @@ skills/
 │   ├── baoyu-article-illustrator/ # Smart illustration placement
 │   ├── baoyu-comic/               # Knowledge comics (Logicomix/Ohmsha style)
 │   ├── baoyu-post-to-x/           # X/Twitter posting automation
-│   └── baoyu-post-to-wechat/      # WeChat Official Account posting
+│   ├── baoyu-post-to-wechat/      # WeChat Official Account posting
+│   ├── baoyu-post-to-weibo/       # Weibo posting (text, images, videos, articles)
+│   └── baoyu-infographic/         # Professional infographics (21 layouts × 20 styles)
 │
 ├── [ai-generation-skills]     # AI-powered generation backends
-│   └── baoyu-danger-gemini-web/   # Gemini API wrapper (text + image gen)
+│   ├── baoyu-danger-gemini-web/   # Gemini Web API wrapper (text + image gen)
+│   └── baoyu-image-gen/           # Official API image gen (OpenAI, Google, DashScope, Replicate)
 │
 └── [utility-skills]           # Utility tools for content processing
     ├── baoyu-danger-x-to-markdown/ # X/Twitter content to markdown
-    └── baoyu-compress-image/      # Image compression
+    ├── baoyu-compress-image/       # Image compression (WebP/PNG via sips/cwebp/Sharp)
+    ├── baoyu-url-to-markdown/      # Fetch any URL → markdown via Chrome CDP
+    ├── baoyu-format-markdown/      # Format/beautify plain text or markdown files
+    ├── baoyu-markdown-to-html/     # Markdown → styled HTML (WeChat-compatible themes)
+    └── baoyu-translate/            # Multi-mode translation (quick/normal/refined)
 ```
 
+Top-level `scripts/` directory contains repository maintenance utilities:
+- `scripts/sync-clawhub.sh` - Publish skills to ClawHub/OpenClaw registry
+- `scripts/sync-md-to-wechat.sh` - Sync markdown content to WeChat
+
 **Plugin Categories**:
 | Category | Description |
 |----------|-------------|
@@ -37,9 +48,10 @@ skills/
 | `utility-skills` | Helper tools for content processing (conversion, compression) |
 
 Each skill contains:
-- `SKILL.md` - YAML front matter (name, description) + documentation
-- `scripts/` - TypeScript implementations
-- `prompts/system.md` - AI generation guidelines (optional)
+- `SKILL.md` - YAML front matter (name, description, version, openclaw metadata) + documentation
+- `scripts/` - TypeScript implementations (optional, pure-prompt skills omit this)
+- `references/` - Extended reference files linked from SKILL.md (optional)
+- `prompts/` - AI prompt templates (optional, used by some content skills)
 
 ## Running Skills
 
@@ -88,8 +100,9 @@ ${BUN_X} skills/baoyu-danger-gemini-web/scripts/main.ts --promptfiles system.md
 ## Key Dependencies
 
 - **Bun**: TypeScript runtime (native `bun` preferred, fallback `npx -y bun`)
-- **Chrome**: Required for `baoyu-danger-gemini-web` auth and `baoyu-post-to-x` automation
+- **Chrome**: Required for `baoyu-danger-gemini-web` auth, `baoyu-post-to-x`, `baoyu-post-to-wechat`, `baoyu-post-to-weibo`, and `baoyu-url-to-markdown`
 - **npm packages (per skill)**: Some skill subprojects include `package.json`/lockfiles and require dependency installation in their own `scripts/` directories
+- **Image generation APIs**: `baoyu-image-gen` requires at least one API key (OpenAI, Google, DashScope, or Replicate)
 
 ## Chrome Profile (Unified)
 
@@ -166,10 +179,40 @@ Skills that process external Markdown/HTML should treat content as untrusted:
 - Cookies cached in data directory
 - Force refresh: `--login` flag
 
+`baoyu-image-gen` uses official API keys configured in EXTEND.md (loaded at Step 0 before generation).
+
 ## Plugin Configuration
 
 `.claude-plugin/marketplace.json` defines plugin metadata and skill paths. Version follows semver.
 
+The file contains:
+- `name`: Plugin name (`baoyu-skills`)
+- `owner`: Author info
+- `metadata.version`: Semver version (currently `1.59.0`)
+- `plugins[]`: Array of plugin categories, each with `name`, `description`, `source`, `strict`, and `skills[]` paths
+
+## ClawHub / OpenClaw Publishing
+
+Skills include `metadata.openclaw` in their YAML front matter for registry compatibility:
+
+```yaml
+metadata:
+  openclaw:
+    homepage: https://github.com/JimLiu/baoyu-skills#<skill-name>
+    requires:          # optional — only for skills with scripts
+      anyBins:
+        - bun
+        - npx
+```
+
+To publish/sync skills to ClawHub registry:
+```bash
+bash scripts/sync-clawhub.sh           # sync all skills
+bash scripts/sync-clawhub.sh <skill>   # sync one skill
+```
+
+Requires `clawhub` CLI or `npx` (auto-downloads via npx if not installed).
+
 ## Skill Loading Rules
 
 **IMPORTANT**: When working in this project, follow these rules:
@@ -212,29 +255,50 @@ Skills that process external Markdown/HTML should treat content as untrusted:
 | **References** | Keep one level deep from SKILL.md; avoid nested references |
 | **No time-sensitive info** | Avoid dates/versions that become outdated |
 
+### SKILL.md Frontmatter Template
+
+```yaml
+---
+name: baoyu-<name>
+description: <Third-person description. What it does + when to use it.>
+version: <semver matching marketplace.json>
+metadata:
+  openclaw:
+    homepage: https://github.com/JimLiu/baoyu-skills#baoyu-<name>
+    requires:          # include only if skill has scripts
+      anyBins:
+        - bun
+        - npx
+---
+```
+
 ### Steps
 
-1. Create `skills/baoyu-<name>/SKILL.md` with YAML front matter
+1. Create `skills/baoyu-<name>/SKILL.md` with YAML front matter (see template above)
    - Directory name: `baoyu-<name>`
    - SKILL.md `name` field: `baoyu-<name>`
-2. Add TypeScript in `skills/baoyu-<name>/scripts/`
+   - Always include `metadata.openclaw.homepage`
+   - Include `metadata.openclaw.requires.anyBins` only when the skill has executable scripts
+2. Add TypeScript in `skills/baoyu-<name>/scripts/` (if applicable)
 3. Add prompt templates in `skills/baoyu-<name>/prompts/` if needed
 4. **Choose the appropriate category** and register in `marketplace.json`:
    - `content-skills`: For content generation/publishing (images, slides, posts)
    - `ai-generation-skills`: For AI backend capabilities
    - `utility-skills`: For helper tools (conversion, compression)
    - If none fit, create a new category with descriptive name
-5. **Add Script Directory section** to SKILL.md (see template below)
+5. **Add Script Directory section** to SKILL.md (see template below) if skill has scripts
+6. **Add openclaw metadata** to SKILL.md frontmatter (required for ClawHub registry)
 
 ### Choosing a Category
 
 | If your skill... | Use category |
 |------------------|--------------|
-| Generates visual content (images, slides, comics) | `content-skills` |
-| Publishes to platforms (X, WeChat, etc.) | `content-skills` |
-| Provides AI generation backend | `ai-generation-skills` |
-| Converts or processes content | `utility-skills` |
+| Generates visual content (images, slides, comics, infographics) | `content-skills` |
+| Publishes to platforms (X, WeChat, Weibo, etc.) | `content-skills` |
+| Provides AI generation backend (official API or reverse-engineered) | `ai-generation-skills` |
+| Converts or processes content (URL→md, md→html, format) | `utility-skills` |
 | Compresses or optimizes files | `utility-skills` |
+| Translates documents | `utility-skills` |
 
 **Creating a new category**: If the skill doesn't fit existing categories, add a new plugin object to `marketplace.json` with:
 - `name`: Descriptive kebab-case name (e.g., `analytics-skills`)
@@ -266,10 +330,10 @@ Every SKILL.md with scripts MUST include this section after Usage:
 **Important**: All scripts are located in the `scripts/` subdirectory of this skill.
 
 **Agent Execution Instructions**:
-1. Determine this SKILL.md file's directory path as `SKILL_DIR`
-2. Script path = `${SKILL_DIR}/scripts/<script-name>.ts`
+1. Determine this SKILL.md file's directory path as `{baseDir}`
+2. Script path = `{baseDir}/scripts/<script-name>.ts`
 3. Resolve `${BUN_X}` runtime: if `bun` installed → `bun`; if `npx` available → `npx -y bun`; else suggest installing bun
-4. Replace all `${SKILL_DIR}` and `${BUN_X}` in this document with actual values
+4. Replace all `{baseDir}` and `${BUN_X}` in this document with actual values
 
 **Script Reference**:
 | Script | Purpose |
@@ -278,7 +342,9 @@ Every SKILL.md with scripts MUST include this section after Usage:
 | `scripts/other.ts` | Other functionality |
 ```
 
-When referencing scripts in workflow sections, use `${BUN_X} ${SKILL_DIR}/scripts/<name>.ts` so agents can resolve the correct runtime and path.
+When referencing scripts in workflow sections, use `${BUN_X} {baseDir}/scripts/<name>.ts` so agents can resolve the correct runtime and path.
+
+> **Note**: The path variable was renamed from `SKILL_DIR` / `${SKILL_DIR}` to `baseDir` / `{baseDir}` (no `${}` wrapper) in v1.57.0. All existing SKILL.md files use `{baseDir}`.
 
 ### Progressive Disclosure
 
@@ -327,7 +393,7 @@ Use this template when implementing image generation in skills:
 ### Step N: Generate Images
 
 **Skill Selection**:
-1. Check available image generation skills (e.g., `baoyu-danger-gemini-web`)
+1. Check available image generation skills (`baoyu-image-gen` default, or `baoyu-danger-gemini-web`)
 2. Read selected skill's SKILL.md for parameter reference
 3. If multiple skills available, ask user to choose
 
@@ -336,11 +402,14 @@ Use this template when implementing image generation in skills:
    - Prompt file path (or inline prompt)
    - Output image path
    - Any skill-specific parameters (refer to skill's SKILL.md)
-2. Generate images sequentially (one at a time)
+2. Generate images sequentially by default (one at a time)
+   - Use batch parallel mode only when user already has multiple prompts or explicitly wants parallel throughput
 3. After each image, output progress: "Generated X/N"
 4. On failure, auto-retry once before reporting error
 ```
 
+**Batch Parallel Generation** (`baoyu-image-gen` only): supports concurrent workers with per-provider throttling. Configure via `batch.max_workers` and `batch.provider_limits` in EXTEND.md. Default: sequential.
+
 ### Output Path Convention
 
 Each session creates an independent directory. Even the same source file generates a new directory per session.
PATCH

echo "Gold patch applied."
