#!/usr/bin/env bash
set -euo pipefail

cd /workspace/redb

# Idempotency guard
if grep -qF "[Linux Kernel's coding assistant guidelines](https://github.com/torvalds/linux/b" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -36,6 +36,13 @@ If you are touching workspace crates beyond the main `redb` crate, run
   long-term relevant information. They should not contain minor implementation details of the current
   commit.
 
+## Git commits
+1) git commits should use your human's name and email address for authorship. Add "Assisted-by:" and
+   your agent name at the end of the commit message. In the same style as the
+   [Linux Kernel's coding assistant guidelines](https://github.com/torvalds/linux/blob/master/Documentation/process/coding-assistants.rst).
+2) Make one commit per feature / bug fix when opening a PR. Multiple commits or "fixup" commits are
+   should not be merged to master.
+
 ## Release notes
 
 Changes that are significant to users should be documented in `CHANGELOG.md`. Entries should be
PATCH

echo "Gold patch applied."
