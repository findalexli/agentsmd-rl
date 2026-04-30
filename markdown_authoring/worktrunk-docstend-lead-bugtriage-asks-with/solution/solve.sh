#!/usr/bin/env bash
set -euo pipefail

cd /workspace/worktrunk

# Idempotency guard
if grep -qF "with this for unexplained failures rather than chaining version/config/repro" ".claude/skills/running-tend/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/running-tend/SKILL.md b/.claude/skills/running-tend/SKILL.md
@@ -84,12 +84,21 @@ If surrounding lines also need updating, note that in your reply.
 
 ## Issue Triage
 
-When a bug may already be fixed, ask the reporter: `wt --version`
-
-When an issue involves config, shell integration, completions, or unexpected
-behavior that could stem from user setup, ask the reporter for
-`wt config show` output. This reveals installed shells, config paths, and
-active settings — essential context for diagnosing config-related problems.
+When you need more information to diagnose a reported bug, the **primary
+ask is `wt -vv <command>`**. Re-running the failing command with `-vv`
+writes `.git/wt/logs/diagnostic.md` — a single report containing wt/git/OS
+versions, shell integration, `wt config show`, `git worktree list
+--porcelain`, and a `trace.log` of every git invocation with its output —
+and prints a `gh gist create --web <path>` hint. One gist URL pasted into
+the issue gives us most of what we'd otherwise ask for piecemeal, so lead
+with this for unexplained failures rather than chaining version/config/repro
+questions across multiple round-trips.
+
+Reach for narrower asks only when the diagnostic is overkill:
+
+- `wt --version` — when the only question is whether a fix has landed.
+- `wt config show` — when the suspicion is purely config/shell-integration
+  and you already have the command + repro.
 
 ### Closing Duplicates
 
PATCH

echo "Gold patch applied."
