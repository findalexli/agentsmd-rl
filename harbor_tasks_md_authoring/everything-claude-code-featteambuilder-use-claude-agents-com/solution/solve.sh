#!/usr/bin/env bash
set -euo pipefail

cd /workspace/everything-claude-code

# Idempotency guard
if grep -qF "1. **`claude agents` command** (primary) \u2014 run `claude agents` to get all agents" "skills/team-builder/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/team-builder/SKILL.md b/skills/team-builder/SKILL.md
@@ -47,24 +47,31 @@ agents/
 
 ## Configuration
 
-Agent directories are probed in order and results are merged:
+Agents are discovered via two methods, merged and deduplicated by agent name:
 
-1. `./agents/**/*.md` + `./agents/*.md` — project-local agents (both depths)
-2. `~/.claude/agents/**/*.md` + `~/.claude/agents/*.md` — global agents (both depths)
+1. **`claude agents` command** (primary) — run `claude agents` to get all agents known to the CLI, including user agents, plugin agents (e.g. `everything-claude-code:architect`), and built-in agents. This automatically covers ECC marketplace installs without any path configuration.
+2. **File glob** (fallback, for reading agent content) — agent markdown files are read from:
+   - `./agents/**/*.md` + `./agents/*.md` — project-local agents
+   - `~/.claude/agents/**/*.md` + `~/.claude/agents/*.md` — global user agents
 
-Results from all locations are merged and deduplicated by agent name. Project-local agents take precedence over global agents with the same name. A custom path can be used instead if the user specifies one.
+Earlier sources take precedence when names collide: user agents > plugin agents > built-in agents. A custom path can be used instead if the user specifies one.
 
 ## How It Works
 
 ### Step 1: Discover Available Agents
 
-Glob agent directories using the probe order above. Exclude README files. For each file found:
+Run `claude agents` to get the full agent list. Parse each line:
+- **Plugin agents** are prefixed with `plugin-name:` (e.g., `everything-claude-code:security-reviewer`). Use the part after `:` as the agent name and the plugin name as the domain.
+- **User agents** have no prefix. Read the corresponding markdown file from `~/.claude/agents/` or `./agents/` to extract the name and description.
+- **Built-in agents** (e.g., `Explore`, `Plan`) are skipped unless the user explicitly asks to include them.
+
+For user agents loaded from markdown files:
 - **Subdirectory layout:** extract the domain from the parent folder name
 - **Flat layout:** collect all filename prefixes (text before the first `-`). A prefix qualifies as a domain only if it appears in 2 or more filenames (e.g., `engineering-security-engineer.md` and `engineering-software-architect.md` both start with `engineering` → Engineering domain). Files with unique prefixes (e.g., `code-reviewer.md`, `tdd-guide.md`) are grouped under "General"
 - Extract the agent name from the first `# Heading`. If no heading is found, derive the name from the filename (strip `.md`, replace hyphens with spaces, title-case)
 - Extract a one-line summary from the first paragraph after the heading
 
-If no agent files are found after probing all locations, inform the user: "No agent files found. Checked: [list paths probed]. Expected: markdown files in one of those directories." Then stop.
+If no agents are found after running `claude agents` and probing file locations, inform the user: "No agents found. Run `claude agents` to verify your setup." Then stop.
 
 ### Step 2: Present Domain Menu
 
PATCH

echo "Gold patch applied."
