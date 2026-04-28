#!/usr/bin/env bash
set -euo pipefail

cd /workspace/narwhal

# Idempotency guard
if grep -qF "Whenever you modify, create, or delete Rust (`.rs`) files, you MUST follow this " "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -7,8 +7,20 @@ You are an expert AI software engineer. Whenever you modify code in this reposit
 - Never submit a protocol-altering code change without a corresponding documentation update.
 - Always review `docs/PROTOCOL.md` before implementing protocol changes to ensure consistency.
 
-## 2. Memory Allocation Rule
+## 2. Memory Allocation & Idiomatic Rust Rule
 - Minimize heap allocations whenever possible. Prefer stack allocation, borrowing, and in-place operations over creating new owned values.
-- Avoid unnecessary `clone()`, `to_string()`, `to_vec()`, or similar calls when a reference or slice would suffice.
+- Avoid unnecessary `clone()`, `to_string()`, `to_vec()`, `unwrap()`, or `expect()` calls when a reference, slice, or proper error handling would suffice.
 - Reuse buffers and collections instead of allocating new ones in hot paths.
 - When allocations are unavoidable, prefer pre-allocated or pooled resources over per-request allocations.
+
+## 3. Rust Formatting & Linting Gates
+Whenever you modify, create, or delete Rust (`.rs`) files, you MUST follow this exact validation loop before considering your task complete and returning control to the user:
+
+1. **Format:** Run `cargo fmt --all` to format the workspace. Do not ask for permission, just run it.
+2. **Lint:** Run `cargo clippy --workspace --all-targets -- -D warnings` (or use `-p <package>` if scoped to a specific crate) to check for idiomatic code and errors.
+3. **Self-Correct:** If Clippy outputs ANY warnings or errors related to your changes:
+   - You must read the error output.
+   - You must apply the fixes suggested by Clippy.
+   - You may use `cargo clippy --fix --allow-dirty --allow-staged` if it helps resolve the issues faster.
+   - You must re-run the `cargo clippy` command to verify the fix worked.
+4. **Completion:** Do not report that you are finished until `cargo fmt` has been run and `cargo clippy` returns a clean, zero-exit-code run with no warnings.
PATCH

echo "Gold patch applied."
