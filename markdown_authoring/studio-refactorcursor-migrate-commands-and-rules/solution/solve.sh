#!/usr/bin/env bash
set -euo pipefail

cd /workspace/studio

# Idempotency guard
if grep -qF "description: Guide for adding new MCP tools with consistent patterns for schemas" ".cursor/skills/add-mcp-tools/SKILL.md" && grep -qF "description: Prepare code for review by running quality checks, creating convent" ".cursor/skills/commit/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/skills/add-mcp-tools/SKILL.md b/.cursor/skills/add-mcp-tools/SKILL.md
@@ -1,5 +1,6 @@
 ---
-alwaysApply: false
+name: add-mcp-tools
+description: Guide for adding new MCP tools with consistent patterns for schemas, tool definitions, registry updates, and Better Auth integration
 ---
 
 # Adding New MCP Tools to MCP Mesh
diff --git a/.cursor/skills/commit/SKILL.md b/.cursor/skills/commit/SKILL.md
@@ -1,5 +1,14 @@
+---
+name: commit
+description: Prepare code for review by running quality checks, creating conventional commits, and opening pull requests. Use when the user wants to commit changes, create a PR, prepare for code review, or asks to commit their work.
+disable-model-invocation: true
+---
+
 I'm getting ready for code review. Please follow these steps:
 
+## 0. Branch Check
+If you're on the `main` branch, create a new feature branch first before making any commits.
+
 ## 1. Quality Assurance Checks
 Run the following commands in order:
 1. bun run fmt
@@ -28,4 +37,4 @@ Use the `gh` CLI tool to create or update the PR. The PR description MUST follow
 - Ensure the PR title follows Conventional Commit format
 
 ## 4. Report Results
-Finally, report the GitHub PR URL.
\ No newline at end of file
+Finally, report the GitHub PR URL.
PATCH

echo "Gold patch applied."
