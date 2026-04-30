#!/usr/bin/env bash
set -euo pipefail

cd /workspace/recce

# Idempotency guard
if grep -qF "- @~/.claude/recce.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -340,46 +340,4 @@ When you modify frontend code and want to test it with the Python backend:
 ---
 
 ## Individual Preferences
-
-Claude Code can load personal/team-specific preferences from `~/.claude/recce.md` to supplement this file.
-
-### What to Include
-
-**Personal config is for:**
-
-- Team conventions (branch naming, commit formats, PR requirements)
-- Code style preferences when multiple valid approaches exist
-- Domain-specific terminology and internal tool names
-- Workflow specifics (CI/CD, deployment processes)
-
-**Keep in main CLAUDE.md:**
-
-- Architecture patterns and critical constraints (applies to all contributors)
-
-### Example Personal Config
-
-Create `~/.claude/recce.md`:
-
-```markdown
-# Personal Preferences for Recce
-
-## Branch Naming
-- Feature: `feature/DRC-XXXX-description`
-- Bugfix: `fix/DRC-XXXX-description`
-
-## Commit Format
-- Use Conventional Commits: `feat(scope): description`
-- Types: feat, fix, refactor, test, docs, chore
-
-## Code Style
-- Python: Prefer f-strings, explicit type hints, pathlib over os.path
-- TypeScript: Functional components, async/await over .then()
-
-## Before Committing
-- Run `make check` and `pytest tests/`
-- Build frontend if JS changed: `cd js && pnpm run build`
-```
-
-**To enable:** Create the file above. Claude Code will automatically load it when working in this repository.
-
-**Reference syntax:** `@~/.claude/recce.md` tells Claude to load preferences from your home directory.
+- @~/.claude/recce.md
PATCH

echo "Gold patch applied."
