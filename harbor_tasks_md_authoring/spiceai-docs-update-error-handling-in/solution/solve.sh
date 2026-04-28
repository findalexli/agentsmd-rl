#!/usr/bin/env bash
set -euo pipefail

cd /workspace/spiceai

# Idempotency guard
if grep -qF "- **NO `.unwrap()` in test code**: All Result unwraps that are not handled with " ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -59,7 +59,8 @@ cargo run -p testoperator -- run bench -p ./test/spicepods/tpch/sf1/federated/du
 ### Error Handling (CRITICAL)
 
 - **Use SNAFU for all errors**: Derive `Snafu` and `Debug` on error enums
-- **NO `.unwrap()` or `.expect()`**: Use proper error handling with `?` operator or `match`
+- **NO `.unwrap()` or `.expect()` in non-test code**: Use proper error handling with `?` operator or `match`
+- **NO `.unwrap()` in test code**: All Result unwraps that are not handled with `?` in tests should use `.expect()` with a sensible message instead
 - **Use `unreachable!()` for truly impossible cases**: Only when you can prove a case is logically impossible
 - **Use `ensure!` macro**: Preferred over manual `if` + `return Err`
 - **Define errors in originating module**: Keep `Error` enum with the code that uses it
@@ -87,9 +88,18 @@ let value = match state {
 // BAD - avoid unwrap and expect
 let value = option.unwrap();
 let value = option.expect("value must be present");
+
+// GOOD - use expect in tests
+#[cfg(test)]
+mod tests {
+  #[test]
+  fn test_thing() {
+    let value = option.expect("value must be present");
+  }
+}
 ```
 
-**Note**: In test code, `.unwrap()` and `.expect()` are allowed since test failures should panic.
+**Note**: In test code, `.expect()` with descriptive messages is preferred over `.unwrap()` since test failures should panic with clear context.
 
 ### Stream Handling (CRITICAL)
 
PATCH

echo "Gold patch applied."
