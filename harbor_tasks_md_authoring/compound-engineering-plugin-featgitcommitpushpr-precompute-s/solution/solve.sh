#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "- [ ] PR description includes Compound Engineered badge with accurate model and " "plugins/compound-engineering/skills/ce-work-beta/SKILL.md" && grep -qF "- [ ] PR description includes Compound Engineered badge with accurate model and " "plugins/compound-engineering/skills/ce-work/SKILL.md" && grep -qF "If the line above resolved to a semantic version (e.g., `2.42.0`), use it as `[V" "plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/ce-work-beta/SKILL.md b/plugins/compound-engineering/skills/ce-work-beta/SKILL.md
@@ -522,7 +522,7 @@ Before creating PR, verify:
 - [ ] PR description includes Post-Deploy Monitoring & Validation section (or explicit no-impact rationale)
 - [ ] Code review completed (inline self-review or full `ce:review`)
 - [ ] PR description includes summary, testing notes, and screenshots
-- [ ] PR description includes Compound Engineered badge with accurate model, harness, and version
+- [ ] PR description includes Compound Engineered badge with accurate model and harness
 
 ## Code Review Tiers
 
diff --git a/plugins/compound-engineering/skills/ce-work/SKILL.md b/plugins/compound-engineering/skills/ce-work/SKILL.md
@@ -449,7 +449,7 @@ Before creating PR, verify:
 - [ ] PR description includes Post-Deploy Monitoring & Validation section (or explicit no-impact rationale)
 - [ ] Code review completed (inline self-review or full `ce:review`)
 - [ ] PR description includes summary, testing notes, and screenshots
-- [ ] PR description includes Compound Engineered badge with accurate model, harness, and version
+- [ ] PR description includes Compound Engineered badge with accurate model and harness
 
 ## Code Review Tiers
 
diff --git a/plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md b/plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md
@@ -346,13 +346,28 @@ When referencing actual GitHub issues or PRs, use the full format: `org/repo#123
 
 Append a badge footer to the PR description, separated by a `---` rule. Do not add one if the description already contains a Compound Engineering badge (e.g., added by another skill like ce-work).
 
+**Plugin version (pre-resolved):** !`jq -r .version "${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json"`
+
+If the line above resolved to a semantic version (e.g., `2.42.0`), use it as `[VERSION]` in the versioned badge below. Otherwise (empty, a literal command string, or an error), use the versionless badge. Do not attempt to resolve the version at runtime.
+
+**Versioned badge** (when version resolved above):
+
 ```markdown
 ---
 
 [![Compound Engineering v[VERSION]](https://img.shields.io/badge/Compound_Engineering-v[VERSION]-6366f1)](https://github.com/EveryInc/compound-engineering-plugin)
 🤖 Generated with [MODEL] ([CONTEXT] context, [THINKING]) via [HARNESS](HARNESS_URL)
 ```
 
+**Versionless badge** (when version is not available):
+
+```markdown
+---
+
+[![Compound Engineering](https://img.shields.io/badge/Compound_Engineering-6366f1)](https://github.com/EveryInc/compound-engineering-plugin)
+🤖 Generated with [MODEL] ([CONTEXT] context, [THINKING]) via [HARNESS](HARNESS_URL)
+```
+
 Fill in at PR creation time:
 
 | Placeholder | Value | Example |
@@ -362,7 +377,6 @@ Fill in at PR creation time:
 | `[THINKING]` | Thinking level (if known) | extended thinking |
 | `[HARNESS]` | Tool running you | Claude Code, Codex, Gemini CLI |
 | `[HARNESS_URL]` | Link to that tool | `https://claude.com/claude-code` |
-| `[VERSION]` | `plugin.json` -> `version` | 2.40.0 |
 
 ### Step 7: Create or update the PR
 
@@ -374,12 +388,14 @@ PR description here
 
 ---
 
-[![Compound Engineering v[VERSION]](https://img.shields.io/badge/Compound_Engineering-v[VERSION]-6366f1)](https://github.com/EveryInc/compound-engineering-plugin)
+[BADGE LINE FROM BADGE SECTION ABOVE]
 🤖 Generated with [MODEL] ([CONTEXT] context, [THINKING]) via [HARNESS](HARNESS_URL)
 EOF
 )"
 ```
 
+Use the versioned or versionless badge line resolved in the Compound Engineering badge section above.
+
 Keep the PR title under 72 characters. The title follows the same convention as commit messages (Step 2).
 
 #### Existing PR (found in Step 3)
PATCH

echo "Gold patch applied."
