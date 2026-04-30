#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "detect the test platform (VSTest or Microsoft.Testing.Platform), identify the" "plugins/dotnet-test/skills/run-tests/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/dotnet-test/skills/run-tests/SKILL.md b/plugins/dotnet-test/skills/run-tests/SKILL.md
@@ -1,6 +1,13 @@
 ---
 name: run-tests
-description: "Guide for running .NET tests with dotnet test. Use when the user needs to execute tests, detect the test platform (VSTest or Microsoft.Testing.Platform), identify the test framework, apply test filters, or troubleshoot test execution. Covers MSTest, xUnit, NUnit, and TUnit across both VSTest and MTP platforms."
+description: >
+  Runs .NET tests with dotnet test. Use when user says "run tests", "execute
+  tests", "dotnet test", "test filter", "tests not running", or needs to
+  detect the test platform (VSTest or Microsoft.Testing.Platform), identify the
+  test framework, apply test filters, or troubleshoot test execution failures.
+  Covers MSTest, xUnit, NUnit, and TUnit across both VSTest and MTP platforms.
+  DO NOT USE FOR: writing or generating test code, CI/CD pipeline
+  configuration, or debugging failing test logic.
 ---
 
 # Run .NET Tests
PATCH

echo "Gold patch applied."
