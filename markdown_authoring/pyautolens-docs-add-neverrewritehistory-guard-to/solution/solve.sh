#!/usr/bin/env bash
set -euo pipefail

cd /workspace/pyautolens

# Idempotency guard
if grep -qF "and any other agent. The \"Initial commit \u2014 fresh start for AI workflow\" pattern" "AGENTS.md" && grep -qF "and any other agent. The \"Initial commit \u2014 fresh start for AI workflow\" pattern" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -50,3 +50,26 @@ NUMBA_CACHE_DIR=/tmp/numba_cache MPLCONFIGDIR=/tmp/matplotlib python -m pytest t
 3. Run the full test suite: `python -m pytest test_autolens/`
 4. Ensure all tests pass before opening a PR.
 5. If changing public API, note the change in your PR description — downstream workspaces may need updates.
+## Never rewrite history
+
+NEVER perform these operations on any repo with a remote:
+
+- `git init` in a directory already tracked by git
+- `rm -rf .git && git init`
+- Commit with subject "Initial commit", "Fresh start", "Start fresh", "Reset
+  for AI workflow", or any equivalent message on a branch with a remote
+- `git push --force` to `main` (or any branch tracked as `origin/HEAD`)
+- `git filter-repo` / `git filter-branch` on shared branches
+- `git rebase -i` rewriting commits already pushed to a shared branch
+
+If the working tree needs a clean state, the **only** correct sequence is:
+
+    git fetch origin
+    git reset --hard origin/main
+    git clean -fd
+
+This applies equally to humans, local Claude Code, cloud Claude agents, Codex,
+and any other agent. The "Initial commit — fresh start for AI workflow" pattern
+that appeared independently on origin and local for three workspace repos is
+exactly what this rule prevents — it costs ~40 commits of redundant local work
+every time it happens.
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -156,3 +156,26 @@ When importing `autolens as al`:
 ## Line Endings — Always Unix (LF)
 
 All files **must use Unix line endings (LF, `\n`)**. Never write `\r\n` line endings.
+## Never rewrite history
+
+NEVER perform these operations on any repo with a remote:
+
+- `git init` in a directory already tracked by git
+- `rm -rf .git && git init`
+- Commit with subject "Initial commit", "Fresh start", "Start fresh", "Reset
+  for AI workflow", or any equivalent message on a branch with a remote
+- `git push --force` to `main` (or any branch tracked as `origin/HEAD`)
+- `git filter-repo` / `git filter-branch` on shared branches
+- `git rebase -i` rewriting commits already pushed to a shared branch
+
+If the working tree needs a clean state, the **only** correct sequence is:
+
+    git fetch origin
+    git reset --hard origin/main
+    git clean -fd
+
+This applies equally to humans, local Claude Code, cloud Claude agents, Codex,
+and any other agent. The "Initial commit — fresh start for AI workflow" pattern
+that appeared independently on origin and local for three workspace repos is
+exactly what this rule prevents — it costs ~40 commits of redundant local work
+every time it happens.
PATCH

echo "Gold patch applied."
