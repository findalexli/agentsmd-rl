#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-skills

# Idempotency guard
if grep -qF "**This is NON-NEGOTIABLE.** Version changes trigger releases. Committing code ch" "remembering/CLAUDE.md" && grep -qF "version: 3.2.1" "remembering/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/remembering/CLAUDE.md b/remembering/CLAUDE.md
@@ -257,17 +257,22 @@ remembering/
 
 ## Development Notes
 
+**🚨 CRITICAL: ALWAYS UPDATE SKILL VERSION WHEN MAKING CODE CHANGES 🚨**
+
+Before ANY commit to this skill, you MUST update `metadata.version` in SKILL.md frontmatter:
+- Bug fixes/cleanup: Patch bump (3.0.0 → 3.0.1)
+- New features/improvements: Minor bump (3.0.0 → 3.1.0)
+- Breaking changes: Major bump (3.0.0 → 4.0.0)
+
+**This is NON-NEGOTIABLE.** Version changes trigger releases. Committing code changes without a version bump means users won't get the update.
+
+Other development guidelines:
 - Keep dependencies minimal (just `requests`)
 - All timestamps are UTC ISO format
 - Tags stored as JSON arrays
 - Soft delete via `deleted_at` column
 - `session_id` currently placeholder ("session")
 - **Always test changes before creating a PR**
-- **Always update SKILL.md version when making changes**:
-  - Bug fixes: Patch bump (3.0.0 → 3.0.1)
-  - New features/improvements: Minor bump (3.0.0 → 3.1.0)
-  - Breaking changes: Major bump (3.0.0 → 4.0.0)
-  - Version is in `metadata.version` field in SKILL.md frontmatter
 
 ## Lessons for Claude Code Agents
 
diff --git a/remembering/SKILL.md b/remembering/SKILL.md
@@ -2,7 +2,7 @@
 name: remembering
 description: Advanced memory operations reference. Basic patterns (profile loading, simple recall/remember) are in project instructions. Consult this skill for background writes, memory versioning, complex queries, edge cases, session scoping, and retention management.
 metadata:
-  version: 3.2.0
+  version: 3.2.1
 ---
 
 > **⚠️ IMPORTANT FOR CLAUDE CODE AGENTS**
PATCH

echo "Gold patch applied."
