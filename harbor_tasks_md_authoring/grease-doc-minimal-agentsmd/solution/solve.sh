#!/usr/bin/env bash
set -euo pipefail

cd /workspace/grease

# Idempotency guard
if grep -qF "GREASE is a Haskell library and command-line tool for under-constrained symbolic" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,29 @@
+# AGENTS.md
+
+GREASE is a Haskell library and command-line tool for under-constrained symbolic
+execution of binaries.
+
+## Haskell
+
+Format, build, and lint after every change.
+
+- Format: `make -j8 -f scripts/lint/Makefile fmt`
+- Build: `cabal build pkg:grease-exe`
+- Lint: `make -j8 -f scripts/lint/Makefile hs`
+- Test: `cd grease-exe && cabal run test:grease-tests`
+
+### Error handling
+
+Read error handling documentation at `doc/dev/errors.md`.
+
+### Writing tests
+
+See `doc/dev/tests.md`.
+
+## `.cbl` files
+
+Read docs at `doc/sexp.md` and `doc/sexp-progs.md`.
+
+## `*shape*.txt` files
+
+Read docs at `doc/shape-dsl.md`.
PATCH

echo "Gold patch applied."
