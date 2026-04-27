#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "![Claude Code](https://img.shields.io/badge/Opus_4.6_(1M,_Extended_Thinking)-D97" "plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md b/plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md
@@ -317,25 +317,27 @@ Append a badge footer to the PR description, separated by a `---` rule. Do not a
 ---
 
 [![Compound Engineering](https://img.shields.io/badge/Built_with-Compound_Engineering-6366f1)](https://github.com/EveryInc/compound-engineering-plugin)
-![HARNESS](https://img.shields.io/badge/HARNESS_SLUG-MODEL_SLUG-COLOR?logo=LOGO&logoColor=white)
+![HARNESS](https://img.shields.io/badge/MODEL_SLUG-COLOR?logo=LOGO&logoColor=white)
 ```
 
-Fill in at PR creation time using the harness and model lookup tables below.
+Fill in at PR creation time using the harness lookup (for logo and color) and model slug below.
 
 **Harness lookup:**
 
-| Harness | `HARNESS_SLUG` | `LOGO` | `COLOR` |
-|---------|---------------|--------|---------|
-| Claude Code | `Claude_Code` | `claude` | `D97757` |
-| Codex | `Codex` | (omit logo param) | `000000` |
-| Gemini CLI | `Gemini_CLI` | `googlegemini` | `4285F4` |
+| Harness | `LOGO` | `COLOR` |
+|---------|--------|---------|
+| Claude Code | `claude` | `D97757` |
+| Codex | (omit logo param) | `000000` |
+| Gemini CLI | `googlegemini` | `4285F4` |
 
 **Model slug:** Replace spaces with underscores in the model name. Append context window and thinking level in parentheses if known, separated by commas. Examples:
 
 - `Opus_4.6_(1M,_Extended_Thinking)`
 - `GPT_5.4_(High)`
 - `Sonnet_4.6_(200K)`
 - `Opus_4.6` (if context and thinking level are unknown)
+- `Gemini_3.1_Pro`
+- `Gemini_3_Flash`
 
 ### Step 7: Create or update the PR
 
@@ -348,7 +350,7 @@ PR description here
 ---
 
 [![Compound Engineering](https://img.shields.io/badge/Built_with-Compound_Engineering-6366f1)](https://github.com/EveryInc/compound-engineering-plugin)
-![Claude Code](https://img.shields.io/badge/Claude_Code-Opus_4.6_(1M,_Extended_Thinking)-D97757?logo=claude&logoColor=white)
+![Claude Code](https://img.shields.io/badge/Opus_4.6_(1M,_Extended_Thinking)-D97757?logo=claude&logoColor=white)
 EOF
 )"
 ```
PATCH

echo "Gold patch applied."
