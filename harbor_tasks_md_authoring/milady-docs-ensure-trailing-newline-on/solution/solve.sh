#!/usr/bin/env bash
set -euo pipefail

cd /workspace/milady

# Idempotency guard
if grep -qF "The principle: **every change must end up as a commit on the current branch in t" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -483,4 +483,4 @@ This is a cleanup for correctness, maintainability, and architectural integrity.
 - **Prefer many small commits over uncommitted changes.** A messy commit history on a pushed branch is recoverable. Lost work is not.
 - **Push proactively when work is meaningful.** A branch that exists only on the local machine is one disk failure away from gone. If a chunk of work is worth keeping, it's worth pushing.
 
-The principle: **every change must end up as a commit on the current branch in the current worktree, and ideally pushed.** No stashes, no branch hopping, no work that exists only in the working tree or in `git stash list`.
\ No newline at end of file
+The principle: **every change must end up as a commit on the current branch in the current worktree, and ideally pushed.** No stashes, no branch hopping, no work that exists only in the working tree or in `git stash list`.
PATCH

echo "Gold patch applied."
