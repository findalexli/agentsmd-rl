#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gitbutler

# Idempotency guard
if grep -qF "4. **Commit early and often** - don't wait for perfection. Unlike traditional gi" "crates/but/skill/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/crates/but/skill/SKILL.md b/crates/but/skill/SKILL.md
@@ -19,6 +19,8 @@ Help users work with GitButler CLI (`but` command) in workspace mode.
 4. **Commit work** → `but commit <branch> -m "message" --files <id>,<id>` (commit specific files by CLI ID)
 5. **Refine** → Use `but absorb` or `but squash` to clean up history
 
+**Commit early, commit often.** Don't hesitate to create commits - GitButler makes editing history trivial. You can always `squash`, `reword`, or `absorb` changes into existing commits later. Small atomic commits are better than large uncommitted changes.
+
 ## After Using Write/Edit Tools
 
 When ready to commit:
@@ -152,7 +154,7 @@ but commit ui-update -m "Update UI" --files <ui-file-id>
 **Committing specific hunks (fine-grained control):**
 
 ```bash
-but diff --json             # See hunk IDs when file has multiple changes
+but diff --json             # See hunk IDs when a file has multiple changes
 but commit <branch> -m "Fix first issue" --files <hunk-id-1>
 but commit <branch> -m "Fix second issue" --files <hunk-id-2>
 ```
@@ -178,7 +180,7 @@ but resolve finish      # Complete resolution
 1. Always start with `but status --json` to understand current state (agents should always use `--json`)
 2. Create a new stack for each independent work theme
 3. Use `--files` to commit specific files directly - no need to stage first
-4. Commit at logical units of work
+4. **Commit early and often** - don't wait for perfection. Unlike traditional git, GitButler makes editing history trivial with `absorb`, `squash`, and `reword`. It's better to have small, atomic commits that you refine later than to accumulate large uncommitted changes.
 5. **Use `--json` flag for ALL commands** when running as an agent - this provides structured, parseable output instead of human-readable text
 6. Use `--dry-run` flags (push, absorb) when unsure
 7. Run `but pull` regularly to stay updated with upstream
PATCH

echo "Gold patch applied."
