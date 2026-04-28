#!/usr/bin/env bash
set -euo pipefail

cd /workspace/terminal.gui

# Idempotency guard
if grep -qF "See `Tests/README.md` for the full list of test projects (including `Integration" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -89,10 +89,22 @@ When in planning mode:
 ```bash
 dotnet restore
 dotnet build --no-restore
+
+# Preferred: parallelizable tests (no static state)
 dotnet test --project Tests/UnitTestsParallelizable --no-build
-dotnet test --project Tests/UnitTests --no-build
+
+# Tests that require process-wide static state (Application.Init, etc.)
+dotnet test --project Tests/UnitTests.NonParallelizable --no-build
+
+# Legacy tests — do NOT add new tests here; candidates for rewrite/deletion
+dotnet test --project Tests/UnitTests.Legacy --no-build
+
+# Run a single test by fully-qualified name
+dotnet test --project Tests/UnitTestsParallelizable --no-build --filter "FullyQualifiedName~MyTestClass.MyTestMethod"
 ```
 
+See `Tests/README.md` for the full list of test projects (including `IntegrationTests`, `StressTests`, `Benchmarks`) and the static-state classification that determines where a new test belongs.
+
 ## Key Concepts
 
 | Concept | Documentation |
@@ -118,7 +130,7 @@ dotnet test --project Tests/UnitTests --no-build
 
 ## Testing
 
-- Prefer `UnitTestsParallelizable` over `UnitTests`
+- Add new tests to `UnitTestsParallelizable`; use `UnitTests.NonParallelizable` only when static state is unavoidable. Never add to `UnitTests.Legacy`.
 - Add comment: `// Claude - Opus 4.5`
 - Never decrease coverage
 - Avoid `Application.Init` in tests
PATCH

echo "Gold patch applied."
