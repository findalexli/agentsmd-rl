#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "- User needs to review or audit existing tests for anti-patterns or test quality" "plugins/dotnet-test/skills/writing-mstest-tests/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/dotnet-test/skills/writing-mstest-tests/SKILL.md b/plugins/dotnet-test/skills/writing-mstest-tests/SKILL.md
@@ -12,13 +12,14 @@ Help users write effective, modern unit tests with MSTest 3.x/4.x using current
 - User wants to write new MSTest unit tests
 - User wants to improve or modernize existing MSTest tests
 - User asks about MSTest assertion APIs, data-driven patterns, or test lifecycle
-- User needs to review MSTest test code for anti-patterns
+- User needs targeted help fixing or modernizing MSTest tests
 
 ## When Not to Use
 
 - User needs to run or execute tests (use the `run-tests` skill)
 - User needs to upgrade from MSTest v1/v2 to v3 (use `migrate-mstest-v1v2-to-v3`)
 - User needs to upgrade from MSTest v3 to v4 (use `migrate-mstest-v3-to-v4`)
+- User needs to review or audit existing tests for anti-patterns or test quality (use `test-anti-patterns`)
 - User needs CI/CD pipeline configuration
 - User is using xUnit, NUnit, or TUnit (not MSTest)
 
@@ -27,7 +28,7 @@ Help users write effective, modern unit tests with MSTest 3.x/4.x using current
 | Input | Required | Description |
 |-------|----------|-------------|
 | Code under test | No | The production code to be tested |
-| Existing test code | No | Current tests to review or improve |
+| Existing test code | No | Current tests to improve or modernize |
 | Test scenario description | No | What behavior the user wants to test |
 
 ## Workflow
PATCH

echo "Gold patch applied."
