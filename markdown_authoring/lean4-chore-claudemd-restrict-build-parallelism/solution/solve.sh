#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lean4

# Idempotency guard
if grep -qF "- ONLY use the project's documented build command: `make -j$(nproc) -C build/rel" ".claude/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/CLAUDE.md b/.claude/CLAUDE.md
@@ -1,18 +1,20 @@
-To build Lean you should use `make -j -C build/release`.
+(In the following, use `sysctl -n hw.logicalcpu` instead of `nproc` on macOS)
+
+To build Lean you should use `make -j$(nproc) -C build/release`.
 
 ## Running Tests
 
 See `doc/dev/testing.md` for full documentation. Quick reference:
 
 ```bash
 # Full test suite (use after builds to verify correctness)
-make -j -C build/release test ARGS="-j$(nproc)"
+make -j$(nproc) -C build/release test ARGS="-j$(nproc)"
 
 # Specific test by name (supports regex via ctest -R)
-make -j -C build/release test ARGS='-R grind_ematch --output-on-failure'
+make -j$(nproc) -C build/release test ARGS='-R grind_ematch --output-on-failure'
 
 # Rerun only previously failed tests
-make -j -C build/release test ARGS='--rerun-failed --output-on-failure'
+make -j$(nproc) -C build/release test ARGS='--rerun-failed --output-on-failure'
 
 # Single test from tests/lean/run/ (quick check during development)
 cd tests/lean/run && ./test_single.sh example_test.lean
@@ -41,7 +43,7 @@ All new tests should go in `tests/lean/run/`. These tests don't have expected ou
 ## Build System Safety
 
 **NEVER manually delete build directories** (build/, stage0/, stage1/, etc.) even when builds fail.
-- ONLY use the project's documented build command: `make -j -C build/release`
+- ONLY use the project's documented build command: `make -j$(nproc) -C build/release`
 - If a build is broken, ask the user before attempting any manual cleanup
 
 ## LSP and IDE Diagnostics
PATCH

echo "Gold patch applied."
