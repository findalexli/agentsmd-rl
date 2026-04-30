#!/usr/bin/env bash
set -euo pipefail

cd /workspace/superpowers

# Idempotency guard
if grep -qF "git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/d" "skills/using-git-worktrees/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/using-git-worktrees/SKILL.md b/skills/using-git-worktrees/SKILL.md
@@ -52,14 +52,14 @@ Which would you prefer?
 
 ### For Project-Local Directories (.worktrees or worktrees)
 
-**MUST verify .gitignore before creating worktree:**
+**MUST verify directory is ignored before creating worktree:**
 
 ```bash
-# Check if directory pattern in .gitignore
-grep -q "^\.worktrees/$" .gitignore || grep -q "^worktrees/$" .gitignore
+# Check if directory is ignored (respects local, global, and system gitignore)
+git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null
 ```
 
-**If NOT in .gitignore:**
+**If NOT ignored:**
 
 Per Jesse's rule "Fix broken things immediately":
 1. Add appropriate line to .gitignore
@@ -145,29 +145,33 @@ Ready to implement <feature-name>
 
 | Situation | Action |
 |-----------|--------|
-| `.worktrees/` exists | Use it (verify .gitignore) |
-| `worktrees/` exists | Use it (verify .gitignore) |
+| `.worktrees/` exists | Use it (verify ignored) |
+| `worktrees/` exists | Use it (verify ignored) |
 | Both exist | Use `.worktrees/` |
 | Neither exists | Check CLAUDE.md → Ask user |
-| Directory not in .gitignore | Add it immediately + commit |
+| Directory not ignored | Add to .gitignore + commit |
 | Tests fail during baseline | Report failures + ask |
 | No package.json/Cargo.toml | Skip dependency install |
 
 ## Common Mistakes
 
-**Skipping .gitignore verification**
+### Skipping ignore verification
+
 - **Problem:** Worktree contents get tracked, pollute git status
-- **Fix:** Always grep .gitignore before creating project-local worktree
+- **Fix:** Always use `git check-ignore` before creating project-local worktree
+
+### Assuming directory location
 
-**Assuming directory location**
 - **Problem:** Creates inconsistency, violates project conventions
 - **Fix:** Follow priority: existing > CLAUDE.md > ask
 
-**Proceeding with failing tests**
+### Proceeding with failing tests
+
 - **Problem:** Can't distinguish new bugs from pre-existing issues
 - **Fix:** Report failures, get explicit permission to proceed
 
-**Hardcoding setup commands**
+### Hardcoding setup commands
+
 - **Problem:** Breaks on projects using different tools
 - **Fix:** Auto-detect from project files (package.json, etc.)
 
@@ -177,7 +181,7 @@ Ready to implement <feature-name>
 You: I'm using the using-git-worktrees skill to set up an isolated workspace.
 
 [Check .worktrees/ - exists]
-[Verify .gitignore - contains .worktrees/]
+[Verify ignored - git check-ignore confirms .worktrees/ is ignored]
 [Create worktree: git worktree add .worktrees/auth -b feature/auth]
 [Run npm install]
 [Run npm test - 47 passing]
@@ -190,15 +194,15 @@ Ready to implement auth feature
 ## Red Flags
 
 **Never:**
-- Create worktree without .gitignore verification (project-local)
+- Create worktree without verifying it's ignored (project-local)
 - Skip baseline test verification
 - Proceed with failing tests without asking
 - Assume directory location when ambiguous
 - Skip CLAUDE.md check
 
 **Always:**
 - Follow directory priority: existing > CLAUDE.md > ask
-- Verify .gitignore for project-local
+- Verify directory is ignored for project-local
 - Auto-detect and run project setup
 - Verify clean test baseline
 
PATCH

echo "Gold patch applied."
