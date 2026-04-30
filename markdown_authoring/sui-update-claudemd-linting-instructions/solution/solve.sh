#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sui

# Idempotency guard
if grep -qF "# Alternatively, run individual lints on specific crates (much faster than linti" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -51,12 +51,16 @@ SUI_SKIP_SIMTESTS=1 cargo nextest run
 # Formats & lints all Rust & Move, run before commit:
 ./scripts/lint.sh
 
-# Alternatively, run individual lints:
-cargo fmt --all -- --check
+# Alternatively, run individual lints on specific crates (much faster than linting the whole repo):
+# For crates in `crates/`: cd into the crate directory and run:
 cargo xclippy
+# For crates in `external-crates/`: cd into the crate directory and run:
+cargo move-clippy
+# For formatting:
+cargo fmt --all -- --check
 ```
 
-`cargo xclippy does not recognize -p option` - This is a known issue with some clippy command variations
+`cargo xclippy` does not recognize the `-p` option - cd into the crate directory instead.
 
 ## High-Level Architecture
 
PATCH

echo "Gold patch applied."
