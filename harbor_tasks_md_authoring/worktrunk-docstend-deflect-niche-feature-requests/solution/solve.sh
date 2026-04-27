#!/usr/bin/env bash
set -euo pipefail

cd /workspace/worktrunk

# Idempotency guard
if grep -qF "- The request benefits a small subset of users or a single reporter's workflow" ".claude/skills/running-tend/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/running-tend/SKILL.md b/.claude/skills/running-tend/SKILL.md
@@ -97,24 +97,24 @@ When an issue is clearly a duplicate, close it after commenting. Use
 `gh issue close <number>` and tell the reporter: if they believe this was
 closed in error, they can let us know and we'll reopen it.
 
-### Suggesting Aliases for Feature Requests
+### Suggesting Aliases for Niche Feature Requests
 
-When a feature request can be addressed with a shell alias or `wt step` alias,
-compose and test one before responding. This lets users try workflows
-immediately rather than waiting for a native flag.
+Deflect narrow feature requests to aliases rather than native flags — this
+keeps the CLI surface small while giving users the behavior immediately.
+Suggest an alias when:
 
-**When to suggest an alias:**
-- The request is for a behavioral variant of an existing command (e.g.,
-  idempotent create-or-switch, auto-push after merge)
-- The behavior can be composed from existing `wt` commands
+- The request benefits a small subset of users or a single reporter's workflow
+  (e.g., idempotent create-or-switch, auto-push after merge)
+- The behavior can be composed from existing `wt` commands or shell primitives
 - A shell one-liner or `wt step` alias covers the use case
 
 **How to respond:**
 1. Draft the alias (shell function or `wt step` alias, whichever fits better)
-2. Test it in a scratch repo — verify it works for both the happy path and the
-   fallback case
+2. Test it in a scratch worktree — verify it works for the happy path and edge
+   cases (e.g., branch already exists, dirty worktree, missing remote)
 3. Post the tested alias in the issue with usage examples
-4. Link to the [aliases docs](https://worktrunk.dev/step/#aliases) for context
+4. Link to the [aliases docs](https://worktrunk.dev/step/#aliases) and
+   [tips & patterns](https://worktrunk.dev/tips-patterns/) for further recipes
 
 ## Weekly Maintenance: MSRV & Toolchain
 
PATCH

echo "Gold patch applied."
