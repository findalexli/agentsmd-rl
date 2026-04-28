#!/usr/bin/env bash
set -euo pipefail

cd /workspace/beads

# Idempotency guard
if grep -qF "- **Compaction Strategies**: `{baseDir}/references/WORKFLOWS.md`" "skills/beads/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/beads/SKILL.md b/skills/beads/SKILL.md
@@ -782,15 +782,15 @@ bd ready  # Uses alternate database
 
 For complex scenarios, see references:
 
-- **Compaction Strategies**: `{baseDir}/references/ADVANCED_WORKFLOWS.md`
+- **Compaction Strategies**: `{baseDir}/references/WORKFLOWS.md`
   - Tier 1/2/ultra compaction for old closed issues
   - Semantic summarization to reduce database size
 
-- **Epic Management**: `{baseDir}/references/ADVANCED_WORKFLOWS.md`
+- **Epic Management**: `{baseDir}/references/WORKFLOWS.md`
   - Nested epics (epics containing epics)
   - Bulk operations on epic children
 
-- **Template System**: `{baseDir}/references/ADVANCED_WORKFLOWS.md`
+- **Template System**: `{baseDir}/references/WORKFLOWS.md`
   - Custom issue templates
   - Template variables and defaults
 
PATCH

echo "Gold patch applied."
