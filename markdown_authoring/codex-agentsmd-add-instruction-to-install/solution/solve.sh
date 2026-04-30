#!/usr/bin/env bash
set -euo pipefail

cd /workspace/codex

# Idempotency guard
if grep -qF "- Install any commands the repo relies on (for example `just`, `rg`, or `cargo-i" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -4,6 +4,7 @@ In the codex-rs folder where the rust code lives:
 
 - Crate names are prefixed with `codex-`. For example, the `core` folder's crate is named `codex-core`
 - When using format! and you can inline variables into {}, always do that.
+- Install any commands the repo relies on (for example `just`, `rg`, or `cargo-insta`) if they aren't already available before running instructions here.
 - Never add or modify any code related to `CODEX_SANDBOX_NETWORK_DISABLED_ENV_VAR` or `CODEX_SANDBOX_ENV_VAR`.
   - You operate in a sandbox where `CODEX_SANDBOX_NETWORK_DISABLED=1` will be set whenever you use the `shell` tool. Any existing code that uses `CODEX_SANDBOX_NETWORK_DISABLED_ENV_VAR` was authored with this fact in mind. It is often used to early exit out of tests that the author knew you would not be able to run given your sandbox limitations.
   - Similarly, when you spawn a process using Seatbelt (`/usr/bin/sandbox-exec`), `CODEX_SANDBOX=seatbelt` will be set on the child process. Integration tests that want to run Seatbelt themselves cannot be run under Seatbelt, so checks for `CODEX_SANDBOX=seatbelt` are also often used to early exit out of tests, as appropriate.
PATCH

echo "Gold patch applied."
