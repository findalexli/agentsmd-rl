#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "**Always run full mode by default.** Proceed directly to Phase 1 unless the user" "plugins/compound-engineering/skills/ce-compound/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/ce-compound/SKILL.md b/plugins/compound-engineering/skills/ce-compound/SKILL.md
@@ -21,41 +21,11 @@ Captures problem solutions while context is fresh, creating structured documenta
 /ce:compound [brief context]    # Provide additional context hint
 ```
 
-## Execution Strategy: Context-Aware Orchestration
+## Execution Strategy
 
-### Phase 0: Context Budget Check
+**Always run full mode by default.** Proceed directly to Phase 1 unless the user explicitly requests compact-safe mode (e.g., `/ce:compound --compact` or "use compact mode").
 
-<critical_requirement>
-**Run this check BEFORE launching any subagents.**
-
-The /compound command is token-heavy - it launches 5 parallel subagents that collectively consume ~10k tokens of context. Running near context limits risks compaction mid-compound, which degrades output quality significantly.
-</critical_requirement>
-
-Before proceeding, the orchestrator MUST:
-
-1. **Assess context usage**: Check how long the current conversation has been running. If there has been significant back-and-forth (many tool calls, large file reads, extensive debugging), context is likely constrained.
-
-2. **Warn the user**:
-   ```
-   ⚠️ Context Budget Check
-
-   /compound launches 5 parallel subagents (~10k tokens). Long conversations
-   risk compaction mid-compound, which degrades documentation quality.
-
-   Tip: For best results, run /compound early in a session - right after
-   verifying a fix, before continuing other work.
-   ```
-
-3. **Offer the user a choice**:
-   ```
-   How would you like to proceed?
-
-   1. Full compound (5 parallel subagents, ~10k tokens) - best quality
-   2. Compact-safe mode (single pass, ~2k tokens) - safe near context limits
-   ```
-
-4. **If the user picks option 1** (or confirms full mode): proceed to Phase 1 below.
-5. **If the user picks option 2** (or requests compact-safe): skip to the **Compact-Safe Mode** section below.
+Compact-safe mode exists as a lightweight alternative — see the **Compact-Safe Mode** section below. It's there if the user wants it, not something to push.
 
 ---
 
PATCH

echo "Gold patch applied."
