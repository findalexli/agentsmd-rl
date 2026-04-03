#!/usr/bin/env bash
set -euo pipefail

cd /workspace/workerd

# Idempotent: skip if already applied
if grep -q 'Python SDK package (frozen)' src/pyodide/AGENTS.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/src/pyodide/AGENTS.md b/src/pyodide/AGENTS.md
index ff9182f2b4a..e6effc5ff02 100644
--- a/src/pyodide/AGENTS.md
+++ b/src/pyodide/AGENTS.md
@@ -15,10 +15,15 @@ Python Workers runtime layer. Replaces Pyodide's loader with a minimal substitut
 | `internal/tar.ts`, `tarfs.ts`                 | Tar archive parsing + read-only filesystem for bundles                                                |
 | `internal/topLevelEntropy/`                   | TS+Python: patches `getRandomValues` with deterministic entropy during import, reseeds before request |
 | `internal/pool/`                              | Emscripten setup in plain V8 isolate; `emscriptenSetup.ts` has NO access to C++ extensions            |
-| `internal/workers-api/`                       | Python SDK package (`pyproject.toml` + `uv.lock` managed)                                             |
+| `internal/workers-api/`                       | Python SDK package (frozen)                                            |
 | `internal/metadata.ts`                        | Config flags: `IS_WORKERD`, `LOCKFILE`, `MAIN_MODULE_NAME`, etc.                                      |
 | `pyodide_extra.capnp`                         | Cap'n Proto schema for Pyodide bundle metadata                                                        |

+## Python SDK
+
+Python SDK (`internal/workers-api/`) now lives in [cloudflare/workers-py](https://github.com/cloudflare/workers-py) and is installed from PyPI. Keep existing code for backward compatibility; new features go to workers-py.
+
+
 ## TESTING

 Tests live in `src/workerd/server/tests/python/`. `py_wd_test.bzl` macro: expands `%PYTHON_FEATURE_FLAGS` template, handles multiple Pyodide versions, snapshot generation/loading, per-version compat flag isolation. Tests are `size="enormous"` by default. Each test generates variants per supported Pyodide version (`0.26.0a2`, newer).
diff --git a/src/pyodide/BUILD.bazel b/src/pyodide/BUILD.bazel
index dc11e043fb3..8d0390ad7ea 100644
--- a/src/pyodide/BUILD.bazel
+++ b/src/pyodide/BUILD.bazel
@@ -64,3 +64,11 @@ py_test(
     ] + glob(["internal/workers-api/src/workers/*"]),
     main = "internal/test_introspection.py",
 )
+
+py_test(
+    name = "unit-test-frozen-sdk",
+    srcs = ["internal/test_frozen_sdk.py"],
+    data = glob(["internal/workers-api/**"]),
+    main = "internal/test_frozen_sdk.py",
+    target_compatible_with = ["@platforms//os:linux"],
+)
diff --git a/src/pyodide/internal/test_frozen_sdk.py b/src/pyodide/internal/test_frozen_sdk.py
new file mode 100644
index 00000000000..174a7da93ed
--- /dev/null
+++ b/src/pyodide/internal/test_frozen_sdk.py
@@ -0,0 +1,54 @@
+"""Test that the in-tree Python SDK (internal/workers-api/) is frozen.
+
+The Python SDK now lives in https://github.com/cloudflare/workers-py and is
+installed from PyPI. The copy in this repository is kept only for backward
+compatibility and MUST NOT be modified.
+
+If this test fails, it means a file under internal/workers-api/ was changed.
+New features should go to cloudflare/workers-py instead. If the change is a
+deliberate backward-compatibility fix, update EXPECTED_HASHES below.
+"""
+
+import hashlib
+import unittest
+from pathlib import Path
+
+SDK_DIR = Path(__file__).parent / "workers-api"
+
+# SHA-256 hashes of every file in the frozen SDK, keyed by path relative to
+# internal/workers-api/.
+# Calculate with: find internal/workers-api -type f -exec sha256sum {} \;
+EXPECTED_HASHES = {
+    "pyproject.toml": "2ba30eeea93f2cf161fce735981b382d2ca1f5aee77e663f447743aabe8575cf",
+    "src/asgi.py": "da171340aa361f733d99d4a1e09c7fe440dd6c79fbca83e4f11d7c42f7622549",
+    "src/workers/__init__.py": "5db8f21adacc3ba625c8763c6e8c47220325109bdc4ec301d76925037844cfd7",
+    "src/workers/_workers.py": "a1e2d9b8199e4bb88c3e89e82dca037772d223bf58bcb1a241d9f03bc54282bd",
+    "src/workers/workflows.py": "9379fdf416da56d2400369165a51b72da83f724aea893ac785285631d09803bf",
+    "uv.lock": "8945fab16bffb1ea1fe5740ca677e40bf8fe28010325e4c389cd11b8a072a9fc",
+}
+
+
+def _sha256(path: Path) -> str:
+    return hashlib.sha256(path.read_bytes()).hexdigest()
+
+
+class TestFrozenSDK(unittest.TestCase):
+    def test_no_files_modified(self):
+        """Ensure no existing SDK files were modified."""
+        for rel_path, expected_hash in sorted(EXPECTED_HASHES.items()):
+            file_path = SDK_DIR / rel_path
+            if not file_path.exists():
+                continue
+            actual_hash = _sha256(file_path)
+            self.assertEqual(
+                actual_hash,
+                expected_hash,
+                f"Python SDK is frozen — {rel_path} was modified. "
+                f"New features belong in cloudflare/workers-py. "
+                f"If this is a deliberate backward-compat fix, update "
+                f"EXPECTED_HASHES in this test.",
+            )
+
+
+if __name__ == "__main__":
+    unittest.main()
diff --git a/src/pyodide/internal/workers-api/src/workers/__init__.py b/src/pyodide/internal/workers-api/src/workers/__init__.py
index 3c311aa2ff6..3eef3e57fc1 100644
--- a/src/pyodide/internal/workers-api/src/workers/__init__.py
+++ b/src/pyodide/internal/workers-api/src/workers/__init__.py
@@ -1,3 +1,6 @@
+# Python SDK for workerd now lives in https://github.com/cloudflare/workers-py
+# All new features should be implemented there and this module is only kept for backward compatibility
+
 from ._workers import (
     Blob,
     BlobEnding,

PATCH

echo "Patch applied successfully."
