#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "allowed-tools: Bash(rover:*) Read Write Edit Glob Grep" "skills/apollo-connectors/SKILL.md" && grep -qF "allowed-tools: Bash(rover:*) Bash(npx:*) Read Write Edit Glob Grep" "skills/apollo-mcp-server/SKILL.md" && grep -qF "allowed-tools: Bash(rover:*) Bash(npm:*) Bash(npx:*) Read Write Edit Glob Grep" "skills/rover/SKILL.md" && grep -qF "- NEVER include `Bash(curl:*)` in `allowed-tools` as it grants unrestricted netw" "skills/skill-creator/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/apollo-connectors/SKILL.md b/skills/apollo-connectors/SKILL.md
@@ -12,7 +12,7 @@ compatibility: Requires rover CLI installed. Works with Claude Code and similar
 metadata:
   author: apollographql
   version: "1.0.0"
-allowed-tools: Bash(rover:*) Bash(curl:*) Read Write Edit Glob Grep
+allowed-tools: Bash(rover:*) Read Write Edit Glob Grep
 ---
 
 # Apollo Connectors Schema Assistant
diff --git a/skills/apollo-mcp-server/SKILL.md b/skills/apollo-mcp-server/SKILL.md
@@ -11,7 +11,7 @@ compatibility: Works with Claude Code, Claude Desktop, Cursor.
 metadata:
   author: apollographql
   version: "1.0.2"
-allowed-tools: Bash(rover:*) Bash(curl:*) Bash(npx:*) Read Write Edit Glob Grep
+allowed-tools: Bash(rover:*) Bash(npx:*) Read Write Edit Glob Grep
 ---
 
 # Apollo MCP Server Guide
diff --git a/skills/rover/SKILL.md b/skills/rover/SKILL.md
@@ -12,7 +12,7 @@ compatibility: Node.js v18+, Linux/macOS/Windows
 metadata:
   author: apollographql
   version: "1.0.1"
-allowed-tools: Bash(rover:*) Bash(curl:*) Bash(npm:*) Bash(npx:*) Read Write Edit Glob Grep
+allowed-tools: Bash(rover:*) Bash(npm:*) Bash(npx:*) Read Write Edit Glob Grep
 ---
 
 # Apollo Rover CLI Guide
diff --git a/skills/skill-creator/SKILL.md b/skills/skill-creator/SKILL.md
@@ -62,7 +62,7 @@ allowed-tools: Read Write Edit Glob Grep
 | `license` | No | License name (e.g., MIT, Apache-2.0). |
 | `compatibility` | No | Environment requirements. Max 500 chars. |
 | `metadata` | No | Key-value pairs for author, version, etc. |
-| `allowed-tools` | No | Space-delimited list of pre-approved tools. |
+| `allowed-tools` | No | Space-delimited list of pre-approved tools. Do not include `Bash(curl:*)`. |
 
 ### Name Rules
 
@@ -266,3 +266,4 @@ Before publishing a skill, verify:
 - PREFER specific examples over abstract explanations
 - PREFER opinionated guidance over listing multiple options
 - USE `allowed-tools` to pre-approve tools the skill needs
+- NEVER include `Bash(curl:*)` in `allowed-tools` as it grants unrestricted network access and enables `curl | sh` remote code execution patterns
PATCH

echo "Gold patch applied."
