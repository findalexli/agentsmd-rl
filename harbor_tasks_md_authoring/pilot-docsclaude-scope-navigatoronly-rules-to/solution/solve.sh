#!/usr/bin/env bash
set -euo pipefail

cd /workspace/pilot

# Idempotency guard
if grep -qF "**If this is an interactive dev session**, use Navigator to plan and Pilot" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -2,9 +2,33 @@
 
 **Navigator plans. Pilot executes.**
 
-## ⚠️ WORKFLOW: Navigator + Pilot Pipeline
-
-**This Claude Code session uses Navigator for planning, Pilot for execution.**
+## Who is reading this file?
+
+This project ships an autonomous executor (Pilot) that runs Claude Code
+against this very repo to implement tickets. That means this `CLAUDE.md`
+is read by two very different kinds of sessions:
+
+1. **Pilot-executor sessions** — spawned by `pilot start` to implement a
+   specific GitHub issue. The prompt describes a concrete task and expects
+   code changes, a commit, and a PR. **In these sessions, YOU ARE Pilot.
+   Implement the task directly. The "Navigator + Pilot pipeline" rules in
+   the next section DO NOT apply — you are the execution leg of that
+   pipeline.** Signals you're in this mode:
+   - Prompt begins with `GitHub Issue #NNN:` or `Task:`
+   - No interactive user is following up
+   - CWD is inside a pilot worktree or a branch named `pilot/GH-*`
+2. **Interactive dev sessions** — a human developer is planning or
+   reviewing work on the Pilot project itself. In these, follow the
+   Navigator + Pilot pipeline below.
+
+When in doubt, look at the incoming prompt: if it hands you a specific
+task with file paths and expected outputs, implement it. If it's a human
+asking open-ended questions about the project, plan via Navigator.
+
+## ⚠️ WORKFLOW: Navigator + Pilot Pipeline (interactive sessions only)
+
+**If this is an interactive dev session**, use Navigator to plan and Pilot
+to execute:
 
 | Phase | Tool | Action |
 |-------|------|--------|
@@ -29,14 +53,18 @@ gh issue list --label pilot --state open
 gh pr view <number> && gh pr merge <number>
 ```
 
-### Rules
+### Rules (interactive sessions)
 
 - ✅ Use `/nav-task` for planning and design
 - ✅ Create GitHub issues with `pilot` label for execution
 - ✅ Review every PR before merging
-- ❌ DO NOT write code directly in this session
-- ❌ DO NOT make commits manually
-- ❌ DO NOT create PRs manually
+- ❌ In *interactive* sessions, do not write code directly — defer to
+  Pilot so the knowledge graph and quality gates run
+- ❌ Do not make commits manually from an interactive planning session
+- ❌ Do not create PRs manually from an interactive planning session
+
+Pilot-executor sessions are the exception: they MUST write code, commit,
+and push — that's their entire job.
 
 **Pilot runs in a separate terminal** (`pilot start --telegram --github`) and auto-picks issues labeled `pilot`.
 
PATCH

echo "Gold patch applied."
