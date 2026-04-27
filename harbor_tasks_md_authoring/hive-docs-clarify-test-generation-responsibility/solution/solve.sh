#!/usr/bin/env bash
set -euo pipefail

cd /workspace/hive

# Idempotency guard
if grep -qF "2. **Generate tests** - The calling agent writes pytest files in `exports/agent_" ".claude/skills/hive/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/hive/SKILL.md b/.claude/skills/hive/SKILL.md
@@ -197,16 +197,18 @@ exports/agent_name/
 
 ### What This Phase Does
 
-Creates comprehensive test suite:
-- Constraint tests (verify hard requirements)
-- Success criteria tests (measure goal achievement)
-- Edge case tests (handle failures gracefully)
-- Integration tests (end-to-end workflows)
+### What This Phase Does
+
+Guides the creation and execution of a comprehensive test suite:
+- Constraint tests
+- Success criteria tests
+- Edge case tests
+- Integration tests
 
 ### Process
 
 1. **Analyze agent** - Read goal, constraints, success criteria
-2. **Generate tests** - Create pytest files in `exports/agent_name/tests/`
+2. **Generate tests** - The calling agent writes pytest files in `exports/agent_name/tests/` using hive-test guidelines and templates
 3. **User approval** - Review and approve each test
 4. **Run evaluation** - Execute tests and collect results
 5. **Debug failures** - Identify and fix issues
PATCH

echo "Gold patch applied."
