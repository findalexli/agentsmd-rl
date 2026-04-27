#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "**Important:** The preprocessor scans the entire SKILL.md as plain text \u2014 it doe" "plugins/compound-engineering/skills/create-agent-skills/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/create-agent-skills/SKILL.md b/plugins/compound-engineering/skills/create-agent-skills/SKILL.md
@@ -97,22 +97,11 @@ Access individual args: `$ARGUMENTS[0]` or shorthand `$0`, `$1`, `$2`.
 
 ### Dynamic Context Injection
 
-The `` !`command` `` syntax runs shell commands before content is sent to Claude:
+Skills support dynamic context injection: prefix a backtick-wrapped shell command with an exclamation mark, and the preprocessor executes it at load time, replacing the directive with stdout. Write an exclamation mark immediately before the opening backtick of the command you want executed (for example, to inject the current git branch, write the exclamation mark followed by `git branch --show-current` wrapped in backticks).
 
-```yaml
----
-name: pr-summary
-description: Summarize changes in a pull request
-context: fork
-agent: Explore
----
-
-## Context
-- PR diff: !`gh pr diff`
-- Changed files: !`gh pr diff --name-only`
+**Important:** The preprocessor scans the entire SKILL.md as plain text — it does not parse markdown. Directives inside fenced code blocks or inline code spans are still executed. If a skill documents this syntax with literal examples, the preprocessor will attempt to run them, causing load failures. To safely document this feature, describe it in prose (as done here) or place examples in a reference file, which is loaded on-demand by Claude and not preprocessed.
 
-Summarize this pull request...
-```
+For a concrete example of dynamic context injection in a skill, see [official-spec.md](references/official-spec.md) § "Dynamic Context Injection".
 
 ### Running in a Subagent
 
PATCH

echo "Gold patch applied."
