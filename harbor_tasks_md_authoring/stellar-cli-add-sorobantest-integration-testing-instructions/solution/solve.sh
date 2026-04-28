#!/usr/bin/env bash
set -euo pipefail

cd /workspace/stellar-cli

# Idempotency guard
if grep -qF "- Test soroban-test integration tests: `cargo test --features it --test it -- in" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -24,6 +24,7 @@ Stellar CLI is a Rust-based command-line tool for interacting with the Stellar n
 
 - Test main soroban-cli library: `cargo test --package soroban-cli --lib` -- takes 52 seconds. NEVER CANCEL.
 - Test individual crates: `cargo test --package <crate-name>` -- typically takes 40 seconds per crate.
+- Test soroban-test integration tests: `cargo test --features it --test it -- integration` -- tests the commands of the cli and is where the bulk of the tests live for this repository. All new commands and changes to commands should include updates or additions to tests in soroban-test.
 - **WARNING**: Full test suite via `make test` requires building WebAssembly test fixtures and consumes significant memory and disk space. It may fail with "No space left on device" in constrained environments.
 
 ### CLI Usage and Validation
PATCH

echo "Gold patch applied."
