#!/usr/bin/env bash
set -euo pipefail

cd /workspace/julia

# Idempotency guard
if grep -qF "JULIA_TEST_FAILFAST=1 ./julia -e 'using Revise; Revise.track(Base); include(\"tes" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -40,6 +40,11 @@ and need to run code with these changes included, you can use `Revise`.
 To do so, run `using Revise; Revise.track(Base)` (or Revise.track with the stdlib you modified).
 The test system supports doing this automatically (see below).
 
+For instance testing Base changes without rebuilding, using failfast, you can run:
+```
+JULIA_TEST_FAILFAST=1 ./julia -e 'using Revise; Revise.track(Base); include("test.jl")'
+```
+
 ## Specific instructions for particular changes
 
 ### Doctests
PATCH

echo "Gold patch applied."
