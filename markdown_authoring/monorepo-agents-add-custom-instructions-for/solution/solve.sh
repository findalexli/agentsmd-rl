#!/usr/bin/env bash
set -euo pipefail

cd /workspace/monorepo

# Idempotency guard
if grep -qF "../AGENTS.md" ".github/copilot-instructions.md" && grep -qF "When reviewing PRs, focus the majority of your effort on correctness and perform" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -0,0 +1 @@
+../AGENTS.md
\ No newline at end of file
diff --git a/AGENTS.md b/AGENTS.md
@@ -148,6 +148,11 @@ cargo llvm-cov --workspace --lcov --output-path lcov.info
 4. Use `just fix-fmt` for formatting
 5. Run full CI checks locally before creating PR
 
+## Reviewing PRs
+When reviewing PRs, focus the majority of your effort on correctness and performance (not style). Pay special attention to bugs
+that can be caused by malicious participants when a function accepts untrusted input. This repository is designed to be
+used in adversarial environments, and as such, we should be extra careful to ensure that the code is robust.
+
 ## Deterministic Async Testing
 Exclusively use the deterministic runtime (`runtime/src/deterministic.rs`) for reproducible async tests:
 ```rust
PATCH

echo "Gold patch applied."
