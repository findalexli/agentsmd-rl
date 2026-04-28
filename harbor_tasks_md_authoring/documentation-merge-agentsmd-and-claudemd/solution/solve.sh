#!/usr/bin/env bash
set -euo pipefail

cd /workspace/documentation

# Idempotency guard
if grep -qF "- **Style**: Follow [12 Rules of Technical Writing](../12-rules-of-technical-wri" ".github/copilot-instructions.md" && grep -qF "This is the official Strapi documentation repository, built with Docusaurus 3. T" "AGENTS.md" && grep -qF "CLAUDE.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -0,0 +1,16 @@
+# Copilot Instructions
+
+This is the Strapi documentation repository (Docusaurus 3, docs.strapi.io).
+Full agent guidance, conventions, and project rules are in [`AGENTS.md`](../AGENTS.md).
+
+## Quick reference
+
+- **Stack**: JavaScript/Node only — no new languages without approval
+- **Dev**: `cd docusaurus && yarn && yarn dev` (port 8080)
+- **Build**: `yarn build` (required before PRs)
+- **Docs format**: MDX with frontmatter (`title`, `description`, `displayed_sidebar`, `tags`)
+- **Style**: Follow [12 Rules of Technical Writing](../12-rules-of-technical-writing.md) and [Style Guide](../STYLE_GUIDE.pdf)
+- **Branch prefixes**: `cms/` for CMS docs, `cloud/` for Cloud docs, `repo/` for everything else
+- **Allowed file types in docs/**: `.md`, `.mdx` only
+- **Code examples**: Must be validated against [strapi/strapi](https://github.com/strapi/strapi)
+- **Commit style**: Imperative mood, capitalized verb, 80 chars max, no `feat:`/`chore:` prefix
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,56 +1,109 @@
 # AGENTS.md (Repository-wide agent guide)
 
-Scope and precedence
+## Scope and precedence
+
 - This file applies to the entire repository.
-- Area‑specific AGENTS files (in `agents/authoring/`) may add or override rules for their scope.
+- Area‑specific AGENTS files (in `agents/`) may add or override rules for their scope.
+
+## Project overview
+
+This is the official Strapi documentation repository, built with Docusaurus 3. The main documentation website is at [docs.strapi.io](https://docs.strapi.io). This repository contains only documentation content — the actual Strapi codebase is in the separate [strapi/strapi](https://github.com/strapi/strapi) repository.
+
+The documentation covers two products with different audiences:
+- **CMS Docs** (`docs/cms/`) — Core Strapi CMS features and APIs
+- **Cloud Docs** (`docs/cloud/`) — Strapi Cloud hosting platform
+
+## Development commands and prerequisites
+
+All development is done in the `/docusaurus` subdirectory (`cd docusaurus`).
+
+### Core commands
+- `yarn && yarn dev` — Install dependencies and start development server (port 8080)
+- `yarn build` — Build the documentation (**required before submitting PRs**)
+- `yarn serve` — Serve the built documentation locally
+
+
+### Content generation and validation
+- `yarn generate-llms` — Generate LLM-specific content files (`docusaurus/scripts/generate-llms.js` → generates `llms.txt`, uses `<Tldr>` when present)
+- `yarn llms:generate-and-validate` — Generate and validate LLM code examples (`docusaurus/scripts/generate-llms-code.js --anchors --check-files` → generates `llms-code.txt`)
+- `yarn validate:llms-code` — Validate existing LLM code examples
+- `docusaurus/scripts/validate-prompts.js` — Validates prompt placeholders/structure
+
+### Other scripts
+- `yarn release-notes` — Generate release notes
+- `yarn redirections-analysis` — Analyze URL redirections
+
+### Prerequisites
+- Node.js >= 18.15.0 <= 22.x.x
+- Yarn >= 1.22.x
+
+## Execution policy and invariants
 
-Execution policy and invariants
 - Stack: prefer JavaScript/Node; do not introduce new languages without approval.
 - Do not modify `llms-full.txt` generation.
 - Enable anchors and file checks by default for code extraction.
 
-Accepted languages and file types
-- Path‑based policy (applies to folders and all subfolders):
-  - `src/` (and `docusaurus/src/` when applicable): allow `.js`, `.jsx`, `.ts`, `.tsx`, `.json`, `.css`, `.scss`, `.html`.
-  - `docs/cms/`, `docs/cloud/`, `docs/snippets/`: allow only `.md`, `.mdx`.
-  - `static/`: allow image assets (`.png`, `.svg`, `.gif`, `.jpg`), `.html`, `.js`.
-  - `.github/workflows/`: allow only `.yml`.
-- Also present elsewhere in the repo: `.scss`, `.css`, image assets (do not expand usage without approval).
-- Not allowed without explicit approval: Python, Ruby, Go, Rust, etc. (no new stacks).
+## Accepted languages and file types
 
-Key scripts and how to run
-- `docusaurus/scripts/generate-llms.js` → generates `llms.txt` (uses <Tldr> when present).
-- `docusaurus/scripts/generate-llms-code.js --anchors --check-files` → generates `llms-code.txt` with section anchors and file existence status.
-- `docusaurus/scripts/validate-prompts.js` → validates prompt placeholders/structure.
+Path‑based policy (applies to folders and all subfolders):
+- `src/` (and `docusaurus/src/`): allow `.js`, `.jsx`, `.ts`, `.tsx`, `.json`, `.css`, `.scss`, `.html`.
+- `docs/cms/`, `docs/cloud/`, `docs/snippets/`: allow only `.md`, `.mdx`.
+- `static/`: allow image assets (`.png`, `.svg`, `.gif`, `.jpg`), `.html`, `.js`.
+- `.github/workflows/`: allow only `.yml`.
+- Also present elsewhere: `.scss`, `.css`, image assets (do not expand usage without approval).
+- Not allowed without explicit approval: Python, Ruby, Go, Rust, etc. (no new stacks).
 
-File map (important paths)
-- AI toolbar: `docusaurus/src/components/AiToolbar/openLLM.js`, `.../config/aiToolsConfig.js`, `.../config/aiPromptTemplates.js`.
-- Generators/validators: `docusaurus/scripts/generate-llms-code.js`, `docusaurus/scripts/generate-llms.js`, `docusaurus/scripts/validate-prompts.js`.
-- Authoring templates: `agents/templates/*.md` (see `agents/templates/INDEX.md`).
-- Components guidance: `agents/templates/components/tabs.md` (Tabs/TabItem rules).
+## Repository structure and file map
 
-Output and communication expectations
-- When asked, paste changed files or generated artifacts.
-- Use bullet lists for unordered information; numbers for sequences.
-- Reference files with repo‑relative clickable paths.
-
-PR and branch workflow
-- Branch naming:
-  - Branches touching only files in `/cms` and `/static` must be prefixed with `/cms`
-  - Branches touching only files in `/cloud` and `/static` must be prefixed with `/cloud`
-  - Other branches must be prefixed with `/repo`
-  - If ambiguous, ask the user how to name the branch; user choice always supersedes auto-branch naming
+```
+/
+├── docusaurus/                 # Main Docusaurus application
+│   ├── docs/                  # Documentation content
+│   │   ├── cms/               # Strapi CMS documentation
+│   │   └── cloud/             # Strapi Cloud documentation
+│   ├── src/                   # React components and custom pages
+│   ├── static/                # Static assets
+│   ├── scripts/               # Build and utility scripts
+│   ├── sidebars.js           # Sidebar configuration
+│   └── docusaurus.config.js  # Main configuration
+├── agents/                    # Documentation review and generation agents
+│   ├── prompts/              # AI agent specifications
+│   ├── templates/            # Content templates
+│   └── authoring/            # Authoring guides
+└── .cursor/rules/            # Cursor IDE rules for documentation agents
+```
 
-Security and tokens
-- Never commit secrets. Use `GITHUB_TOKEN` env var if needed; least privilege; rotate/revoke after use.
+### Key files
+- AI toolbar: `docusaurus/src/components/AiToolbar/openLLM.js`, `.../config/aiToolsConfig.js`, `.../config/aiPromptTemplates.js`
+- Generators/validators: `docusaurus/scripts/generate-llms-code.js`, `docusaurus/scripts/generate-llms.js`, `docusaurus/scripts/validate-prompts.js`
+- Authoring templates: `agents/templates/*.md` (see `agents/templates/INDEX.md`)
+- Agent prompts: `agents/prompts/` (see table in Documentation Review System section)
+- Components guidance: `agents/templates/components/tabs.md` (Tabs/TabItem rules)
+- Configuration: `docusaurus.config.js`, `sidebars.js`, `package.json`
+
+## Writing guidelines and content validation
+
+### Style and quality
+- Follow the [12 Rules of Technical Writing](12-rules-of-technical-writing.md)
+- Use the [Style Guide](STYLE_GUIDE.pdf) for formatting conventions
+- Disable linters/auto-formatters before saving to prevent rendering issues
+
+### Content structure
+- Use MDX format (Markdown + React components)
+- Include proper frontmatter with `title`, `description`, `displayed_sidebar`, `tags`
+- Use sentence case for headings
+- Include `<Tldr>` components for page summaries
+- Use numbered lists for procedures, bullet points for features/options
+
+### Content validation
+- Auto-generated files: `llms.txt`, `llms-full.txt`, `llms-code.txt` — content is optimized for AI consumption while maintaining human readability
+- All code examples produced by AI agents MUST be validated against the actual [strapi/strapi](https://github.com/strapi/strapi) codebase
+- Include both JavaScript and TypeScript variants when applicable
+- Build process: LLM content generation → code example validation → link checking → static site generation
 
-Links
-- Contributing guide: CONTRIBUTING.md
-- Style guide (PDF): STYLE_GUIDE.pdf
-- 12 Rules of Technical Writing: 12-rules-of-technical-writing.md (canonical)
-- External reference: https://strapi.notion.site/12-Rules-of-Technical-Writing-c75e080e6b19432287b3dd61c2c9fa04
+## Documentation Review System
 
-## Directory of AGENTS guides
+### Directory of AGENTS guides
 
 - CMS (canonical): `agents/authoring/AGENTS.cms.md`
 - CMS – How‑to Guides: `agents/authoring/AGENTS.cms.guides.md`
@@ -63,29 +116,23 @@ Links
 
 The `agents/templates/README.md` explains the purpose of the templates directory (authoring skeletons) and lists all templates with links.
 
-## Documentation Review System
-
-Specialized prompts for reviewing and creating Strapi documentation. Located in `agents/prompts/`.
-
-| Prompt | Path | Status | Purpose |
-|--------|------|--------|---------|
-| **Orchestrator** | `agents/prompts/orchestrator.md` | ✅ Available | Coordinates Review and Create workflows |
-| **Router** | `agents/prompts/router.md` | ✅ Available | Identifies doc type, determines placement, loads template and authoring guide |
-| **Outliner** | `agents/prompts/outliner.md` | ✅ Available | Routes to Outline Checker, UX Analyzer, or Outline Generator |
-| **Outline Checker** | `agents/prompts/outline-checker.md` | ✅ Available | Ensures template compliance, frontmatter, heading hierarchy |
-| **Outline UX Analyzer** | `agents/prompts/outline-ux-analyzer.md` | ✅ Available | Checks reader experience, section order, cognitive load |
-| **Style Checker** | `agents/prompts/style-checker.md` | ✅ Available | Ensures compliance to 12 Rules of Technical Writing |
-| **Outline Generator** | `agents/prompts/outline-generator.md` | ✅ Available | Creates outlines from source material (Notion, Jira, specs) |
-| **Drafter** | `agents/prompts/drafter.md` | ✅ Available | Drafts documentation based on inputs from Router and Outliner |
-| **Integrity Checker** | `agents/prompts/integrity-checker.md` | ✅ Available | Coordinates technical verification (code examples, cross-page coherence) |
+### Specialized prompts
 
-### Shared Resources
+Located in `agents/prompts/`. Cursor IDE wrappers are in `.cursor/rules/`.
 
-The `agents/prompts/shared/` folder contains guides used by multiple prompts:
+| Prompt | Path | Purpose |
+|--------|------|---------|
+| **Orchestrator** | `agents/prompts/orchestrator.md` | Coordinates Review and Create workflows |
+| **Router** | `agents/prompts/router.md` | Identifies doc type, determines placement, loads template and authoring guide |
+| **Outliner** | `agents/prompts/outliner.md` | Routes to Outline Checker, UX Analyzer, or Outline Generator |
+| **Outline Checker** | `agents/prompts/outline-checker.md` | Ensures template compliance, frontmatter, heading hierarchy |
+| **Outline UX Analyzer** | `agents/prompts/outline-ux-analyzer.md` | Checks reader experience, section order, cognitive load |
+| **Outline Generator** | `agents/prompts/outline-generator.md` | Creates outlines from source material (Notion, Jira, specs) |
+| **Style Checker** | `agents/prompts/style-checker.md` | Ensures compliance to 12 Rules of Technical Writing |
+| **Drafter** | `agents/prompts/drafter.md` | Drafts documentation based on inputs from Router and Outliner |
+| **Integrity Checker** | `agents/prompts/integrity-checker.md` | Coordinates technical verification (code examples, cross-page coherence) |
 
-| Resource | Path | Purpose |
-|----------|------|---------|
-| **GitHub MCP Usage** | `agents/prompts/shared/github-mcp-usage.md` | How to fetch PR content using GitHub MCP tools |
+Shared resources: `agents/prompts/shared/github-mcp-usage.md` (how to fetch PR content using GitHub MCP tools).
 
 ### Workflows
 
@@ -102,50 +149,56 @@ Router → Outliner (Generator) → Drafter → Style Checker → Integrity Chec
 ### Usage
 
 These prompts are designed for use in:
-- **Claude Projects**: Import prompts as project knowledge
-- **Claude.ai / ChatGPT**: Copy prompt content into the conversation
-- **API integrations**: Use as system prompts
+- **Claude Code / Claude Projects**: Import prompts as project knowledge
+- **Cursor IDE**: Use the `.cursor/rules/*.mdc` wrappers
+- **Other AI tools (Copilot, Cline, Windsurf…)**: Copy prompt content or use as system prompts
 
 See `agents/prompts/README.md` for detailed usage instructions.
 
-## General git usage rules
-
-(see git-rules.md for details)
-
-- Commit messages
-  - Start with a capitalized action verb in imperative mood (e.g., Add, Update, Fix).
-  - Keep to 80 characters max; be succinct about what/why.
-  - Do not prefix with "feat:", "chore:", or similar keywords.
-  - Do not use PR-style phrasing (never start a commit with "This PR …").
-
-- PR descriptions
-  - Start with "This PR …" followed by a one‑sentence summary.
-  - End the sentence with a period, or a colon if followed by bullets.
-  - Use bullet points for optional extra details.
-  - Do not add sections like Summary/Changes/Motivation/How to validate.
-  - Do not include manual test instructions unless absolutely necessary.
-  - Screenshots or GIFs are welcome when they help.
-
-- Branch and history safety
-  - Never force‑push, rebase shared branches, or push to `main` without explicit maintainer consent.
-  - Never delete local or remote branches unless explicitly instructed by the maintainer.
-  - Get explicit consent before any history rewrite (rebase, squash, filter‑branch).
-  - Prefer creating a new branch over rewriting history; propose the plan first.
-  - When asked to stay low profile, do not open PRs unless explicitly requested; share progress in this chat.
-
-- Pushing and PRs
-  - When pushing a new branch, set upstream (no PR auto‑creation).
-  - Open PRs only when requested and follow the description rules above.
-  - Titles must not start with feat:/chore:/fix:; keep titles short and clear.
-  - For the full, detailed guidance and examples, see: `git-rules.md`.
-
-## 12 Rules (Overview)
-
-- Canonical in-repo source: `12-rules-of-technical-writing.md`.
-- Full text (external): https://strapi.notion.site/12-Rules-of-Technical-Writing-c75e080e6b19432287b3dd61c2c9fa04
-- Summary highlights:
-  - Write for the audience; document the obvious.
-  - Use a direct, neutral tone and simple English.
-  - Be concise: short sentences and clear sectioning.
-  - Procedures use numbered steps; unordered info uses bullets; complex lists use tables.
-  - Avoid ambiguity; keep terminology consistent; define acronyms once; add visuals when helpful.
\ No newline at end of file
+## PR, branch, and git rules
+
+See [`git-rules.md`](git-rules.md) for all commit, PR, and branch safety conventions.
+
+### Branch naming
+- `cms/` — branches touching only `docs/cms/` and `static/`
+- `cloud/` — branches touching only `docs/cloud/` and `static/`
+- `repo/` — everything else
+- If ambiguous, ask the user; user choice always supersedes auto-branch naming
+
+### Security
+
+**Always:**
+- Reference where secrets live (env vars, vault), never the secrets themselves.
+- When using tokens or API keys: least privilege; rotate/revoke after use.
+
+**Ask user first:**
+- Installing or removing dependencies (`yarn add`, `yarn remove`).
+- Modifying CI/CD config (`.github/workflows/`).
+- Deleting files.
+- Pushing to remote or creating PRs.
+
+**Never:**
+- Commit secrets, API keys, tokens, passwords, or `.env` files.
+- Hardcode credentials in source files.
+- Modify `node_modules/` or other vendor directories.
+- Run destructive commands (`rm -rf`, `git push --force`) without explicit approval.
+- Remove failing tests without explicit approval.
+
+## Output and communication expectations
+
+- When asked, paste changed files or generated artifacts.
+- Use bullet lists for unordered information; numbers for sequences.
+- Reference files with repo‑relative clickable paths.
+
+## Links and references
+
+- Contributing guide: `CONTRIBUTING.md`
+- Style guide (PDF): `STYLE_GUIDE.pdf`
+- 12 Rules of Technical Writing: `12-rules-of-technical-writing.md` ([external](https://strapi.notion.site/12-Rules-of-Technical-Writing-c75e080e6b19432287b3dd61c2c9fa04))
+
+### 12 Rules (overview)
+- Write for the audience; document the obvious.
+- Use a direct, neutral tone and simple English.
+- Be concise: short sentences and clear sectioning.
+- Procedures use numbered steps; unordered info uses bullets; complex lists use tables.
+- Avoid ambiguity; keep terminology consistent; define acronyms once; add visuals when helpful.
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,155 +1 @@
-# CLAUDE.md
-
-This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
-
-## Project Overview
-
-This is the official Strapi documentation repository, built with Docusaurus 3. The main documentation website is hosted at [docs.strapi.io](https://docs.strapi.io). This repository contains only documentation content - the actual Strapi codebase is in the separate [strapi/strapi](https://github.com/strapi/strapi) repository.
-
-## Development Commands
-
-All development should be done in the `/docusaurus` subdirectory:
-
-```bash
-cd docusaurus
-```
-
-### Core Commands
-
-- `yarn && yarn dev` - Install dependencies and start development server (port 8080)
-- `yarn build` - Build the documentation (required before submitting PRs)
-- `yarn serve` - Serve the built documentation locally
-- `yarn clear` - Clear Docusaurus cache
-
-### Content Generation
-- `yarn generate-llms` - Generate LLM-specific content files
-- `yarn llms:generate-and-validate` - Generate and validate LLM code examples
-- `yarn validate:llms-code` - Validate existing LLM code examples
-
-### Release and Scripts
-- `yarn release-notes` - Generate release notes
-- `yarn redirections-analysis` - Analyze URL redirections
-
-### Prerequisites
-- Node.js >= 18.15.0 <= 22.x.x
-- Yarn >= 1.22.x
-- Always run `yarn build` before submitting pull requests to ensure no broken links
-
-## Repository Structure
-
-```
-/
-├── docusaurus/                 # Main Docusaurus application
-│   ├── docs/                  # Documentation content
-│   │   ├── cms/               # Strapi CMS documentation
-│   │   └── cloud/             # Strapi Cloud documentation
-│   ├── src/                   # React components and custom pages
-│   ├── static/                # Static assets
-│   ├── scripts/               # Build and utility scripts
-│   ├── sidebars.js           # Sidebar configuration
-│   └── docusaurus.config.js  # Main configuration
-├── agents/                    # Documentation review and generation agents
-│   ├── prompts/              # AI agent specifications
-│   ├── templates/            # Content templates
-│   └── authoring/            # Authoring guides
-└── .cursor/rules/            # Cursor IDE rules for documentation agents
-```
-
-## Documentation Architecture
-
-The documentation is split into two main sections:
-- **CMS Docs** (`/docs/cms/`) - Core Strapi CMS features and APIs
-- **Cloud Docs** (`/docs/cloud/`) - Strapi Cloud hosting platform
-
-### Content Organization
-- Use branch prefix `cms/` for CMS-related changes
-- Use branch prefix `cloud/` for Cloud-related changes
-- Use branch prefix `repo/` for repository-wide changes
-
-## Writing Guidelines
-
-### Style and Quality
-- Follow the [12 Rules of Technical Writing](12-rules-of-technical-writing.md)
-- Use the [Style Guide](STYLE_GUIDE.pdf) for formatting conventions
-- Disable linters/auto-formatters before saving to prevent rendering issues
-
-### Content Structure
-- Use MDX format (Markdown + React components)
-- Include proper frontmatter with `title`, `description`, `displayed_sidebar`, `tags`
-- Use sentence case for headings
-- Include `<Tldr>` components for page summaries
-- Use numbered lists for procedures, bullet points for features/options
-
-## Documentation Agent System
-
-This repository includes a comprehensive AI-powered documentation workflow system. **Start with `AGENTS.md`** - it's the main entry point and directory for the entire system.
-
-### System Architecture
-
-- **`AGENTS.md`** - Main directory and entry point, explains the complete system
-- **`agents/prompts/`** - Core agent specifications for review and content creation workflows
-- **`agents/templates/`** - Content templates for different documentation types
-- **`agents/authoring/`** - Area-specific authoring guides (CMS, Cloud, APIs, etc.)
-- **`.cursor/rules/`** - Cursor IDE implementations (platform-specific wrappers)
-
-### Available Agents (in `agents/prompts/`)
-
-- **Orchestrator** - Coordinates Review and Create workflows
-- **Router** - Identifies document type, determines placement, loads templates
-- **Outliner** - Handles all documentation structure tasks with three specialized sub-prompts:
-  - **Outline Checker** - Ensures template compliance, frontmatter, heading hierarchy
-  - **Outline UX Analyzer** - Checks reader experience, section order, cognitive load
-  - **Outline Generator** - Creates outlines from source material (Notion, Jira, specs)
-- **Style Checker** - Enforces the 12 Rules of Technical Writing and Strapi conventions
-- **Drafter** - Drafts documentation based on inputs from Router and Outliner
-- **Integrity Checker** - Coordinates technical verification with two specialized sub-checks:
-  - **Code Verifier** - Verifies code examples and technical claims against the Strapi codebase
-  - **Coherence Checker** - Verifies cross-page consistency, links, and terminology
-
-### Workflows
-
-**Review Mode**: `Router → Outliner (Checker) → Style Checker → Integrity Checker`
-**Create Mode**: `Router → Outliner (Generator) → Drafter → Style Checker → Integrity Checker`
-
-## Key Configuration Files
-
-- `docusaurus.config.js` - Main Docusaurus configuration
-- `sidebars.js` - Navigation structure definition
-- `package.json` - Dependencies and build scripts
-- `.cursor/rules/` - AI agent specifications for Cursor IDE
-- `agents/prompts/` - Standalone AI agent specifications
-
-## Content Validation
-
-### LLMs Integration
-The repository includes special handling for LLM (Large Language Model) integrations:
-- Auto-generated files: `llms.txt`, `llms-code.txt`
-- Validation scripts ensure code examples are accurate
-- Content is optimized for AI consumption while maintaining human readability
-
-### Build Process
-The build process includes:
-1. LLM content generation
-2. Code example validation
-3. Link checking
-4. Static site generation
-
-### Code Examples
-- All code examples produced by AI agents MUST be validated against the actual Strapi codebase
-- Use the integrity checker to verify technical accuracy
-- Include both JavaScript and TypeScript variants when applicable
-
-## Branch and PR Conventions
-
-- Target the `main` branch for most pull requests
-- Use descriptive branch names with appropriate prefixes
-- Add `flag: merge pending release` label for release-dependent content
-- Build locally with `yarn build` before submitting PRs
-- Use draft PRs for incremental work
-
-## Important Notes
-
-- **No Strapi codebase in this repo** - Code verification requires access to the separate [strapi/strapi](https://github.com/strapi/strapi) repository
-- **Docusaurus-specific** - Uses Docusaurus 3 with custom plugins and components
-- **AI-enhanced workflow** - Extensive agent system for content review and generation
-- **Multi-product docs** - Covers both CMS and Cloud products with different audiences
\ No newline at end of file
+@AGENTS.md
PATCH

echo "Gold patch applied."
