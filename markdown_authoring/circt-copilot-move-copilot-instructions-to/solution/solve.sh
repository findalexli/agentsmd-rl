#!/usr/bin/env bash
set -euo pipefail

cd /workspace/circt

# Idempotency guard
if grep -qF "- Always run `clang-format` on C++ code changes and `yapf` on Python code change" "AGENTS.md" && grep -qF "The GTest-based unit tests live in `lib/Dialect/ESI/runtime/tests/cpp` and they " "lib/Dialect/ESI/runtime/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -19,5 +19,4 @@
 - For PyCDE and the ESI runtime, add `-DCIRCT_ENABLE_FRONTENDS=PyCDE -DESI_RUNTIME=ON` (keep Python bindings on). Test with `ninja -C build check-pycde` (PyCDE only) and `ninja -C build check-pycde-integration` (these integration tests exercise both PyCDE and the ESI runtime and are the only ESIRuntime tests).
 - Prefer the integration image and the setup steps workflow for reliable dependencies; only fall back to host builds when explicitly requested.
 - When running in local agent mode, try to keep all temporary file writes and reads inside the workspace (in a temp folder) to avoid asking the user for permissions to access files outside the repo.
-
-- When working on the ESI runtime (anything under `lib/Dialect/ESI/runtime`), use the instructions in `.github/copilot-skills-esi-runtime.md` to build and test the runtime independently of a full CIRCT build. This is much faster and is the recommended workflow for runtime-only changes.
+- Always run `clang-format` on C++ code changes and `yapf` on Python code changes.
diff --git a/lib/Dialect/ESI/runtime/AGENTS.md b/lib/Dialect/ESI/runtime/AGENTS.md
@@ -97,7 +97,7 @@ Only change infrastructure or test harness files when there is a demonstrated pr
 
 ### GTest unit tests
 
-The GTest-based unit tests live in `unittests/Dialect/ESI/runtime/` and require a full CIRCT build (they link against `esiaccel::ESICppRuntime` via the CIRCT cmake infrastructure). They can't be built from the standalone runtime cmake.
+The GTest-based unit tests live in `lib/Dialect/ESI/runtime/tests/cpp` and they are built with the ESIRuntimeCppTests target. They can be run independently or they are run by pytest if the binary is present.
 
 ## Key architecture notes
 
PATCH

echo "Gold patch applied."
