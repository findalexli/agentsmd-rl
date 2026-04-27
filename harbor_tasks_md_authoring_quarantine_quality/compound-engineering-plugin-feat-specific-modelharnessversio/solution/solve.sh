#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "\ud83e\udd16 Generated with [MODEL] via [HARNESS](HARNESS_URL) + Compound Engineering v[VER" "CLAUDE.md" && grep -qF "[![Compound Engineering v[VERSION]](https://img.shields.io/badge/Compound_Engine" "plugins/compound-engineering/skills/ce-work/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -359,14 +359,27 @@ Follow these patterns for commit messages:
 - `Fix [issue]` - Bug fixes
 - `Simplify [component] to [improvement]` - Refactoring
 
-Include the Claude Code footer:
+Include the attribution footer (fill in your actual values):
 
 ```
-🤖 Generated with [Claude Code](https://claude.com/claude-code)
+🤖 Generated with [MODEL] via [HARNESS](HARNESS_URL) + Compound Engineering v[VERSION]
 
-Co-Authored-By: Claude <noreply@anthropic.com>
+Co-Authored-By: [MODEL] ([CONTEXT] context, [THINKING]) <noreply@anthropic.com>
 ```
 
+**Fill in at commit/PR time:**
+
+| Placeholder | Value | Example |
+|-------------|-------|---------|
+| Placeholder | Value | Example |
+|-------------|-------|---------|
+| `[MODEL]` | Model name | Claude Opus 4.6, GPT-5.4 |
+| `[CONTEXT]` | Context window (if known) | 200K, 1M |
+| `[THINKING]` | Thinking level (if known) | extended thinking |
+| `[HARNESS]` | Tool running you | Claude Code, Codex, Gemini CLI |
+| `[HARNESS_URL]` | Link to that tool | `https://claude.com/claude-code` |
+| `[VERSION]` | `plugin.json` → `version` | 2.40.0 |
+
 ## Resources to search for when needing more information
 
 - [Claude Code Plugin Documentation](https://docs.claude.com/en/docs/claude-code/plugins)
diff --git a/plugins/compound-engineering/skills/ce-work/SKILL.md b/plugins/compound-engineering/skills/ce-work/SKILL.md
@@ -228,13 +228,28 @@ This command takes a work document (plan, specification, or todo file) and execu
 
    Brief explanation if needed.
 
-   🤖 Generated with [Claude Code](https://claude.com/claude-code)
+   🤖 Generated with [MODEL] via [HARNESS](HARNESS_URL) + Compound Engineering v[VERSION]
 
-   Co-Authored-By: Claude <noreply@anthropic.com>
+   Co-Authored-By: [MODEL] ([CONTEXT] context, [THINKING]) <noreply@anthropic.com>
    EOF
    )"
    ```
 
+   **Fill in at commit/PR time:**
+
+   | Placeholder | Value | Example |
+   |-------------|-------|---------|
+   | Placeholder | Value | Example |
+   |-------------|-------|---------|
+   | `[MODEL]` | Model name | Claude Opus 4.6, GPT-5.4 |
+   | `[CONTEXT]` | Context window (if known) | 200K, 1M |
+   | `[THINKING]` | Thinking level (if known) | extended thinking |
+   | `[HARNESS]` | Tool running you | Claude Code, Codex, Gemini CLI |
+   | `[HARNESS_URL]` | Link to that tool | `https://claude.com/claude-code` |
+   | `[VERSION]` | `plugin.json` → `version` | 2.40.0 |
+
+   Subagents creating commits/PRs are equally responsible for accurate attribution.
+
 2. **Capture and Upload Screenshots for UI Changes** (REQUIRED for any UI work)
 
    For **any** design changes, new views, or UI modifications, you MUST capture and upload screenshots:
@@ -308,7 +323,8 @@ This command takes a work document (plan, specification, or todo file) and execu
 
    ---
 
-   [![Compound Engineered](https://img.shields.io/badge/Compound-Engineered-6366f1)](https://github.com/EveryInc/compound-engineering-plugin) 🤖 Generated with [Claude Code](https://claude.com/claude-code)
+   [![Compound Engineering v[VERSION]](https://img.shields.io/badge/Compound_Engineering-v[VERSION]-6366f1)](https://github.com/EveryInc/compound-engineering-plugin)
+   🤖 Generated with [MODEL] ([CONTEXT] context, [THINKING]) via [HARNESS](HARNESS_URL)
    EOF
    )"
    ```
@@ -445,7 +461,7 @@ Before creating PR, verify:
 - [ ] Commit messages follow conventional format
 - [ ] PR description includes Post-Deploy Monitoring & Validation section (or explicit no-impact rationale)
 - [ ] PR description includes summary, testing notes, and screenshots
-- [ ] PR description includes Compound Engineered badge
+- [ ] PR description includes Compound Engineered badge with accurate model, harness, and version
 
 ## When to Use Reviewer Agents
 
PATCH

echo "Gold patch applied."
