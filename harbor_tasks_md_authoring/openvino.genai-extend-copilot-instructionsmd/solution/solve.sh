#!/usr/bin/env bash
set -euo pipefail

cd /workspace/openvino.genai

# Idempotency guard
if grep -qF "16. Assumptions on the user's behalf aren't allowed. For example, the implementa" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -25,20 +25,23 @@ Follow these rules when writing, modifying, or reviewing code in this repository
 3. Avoid copies: large data structures (like tensors) must be passed by reference or moved, not copied.
 4. Pass non-fundamental values by `const` reference wherever possible.
 5. Exceptions: use `OPENVINO_ASSERT(condition, ...)` for checks instead of `if` + `OPENVINO_THROW(...)` or `throw`.
-6. Formatting & Safety:
+6. Avoid redundant inline comments next to `OPENVINO_ASSERT()` and `OPENVINO_THROW()`; the error message argument must be clear and self-explanatory.
+7. Formatting & Safety:
    - No `using namespace std;`.
    - No `auto` for primitive types where it obscures readability.
    - Use `const` and `constexpr` wherever possible.
-7. Follow constructors and member initializer lists style instead of direct assignments in the constructor body.
-8. When initial container values are known upfront, prefer initializer-list / brace-initialization over constructing an empty container and immediately inserting values.
-9. Make sure the function names are descriptive.
-10. Check for variables with different names but similar meaning or aliasing.
-11. Avoid duplicate code. Ensure that common functionality is extracted into reusable functions or utilities.
-12. Avoid pronouns in comments and names to make the statements concise.
-13. Unused functions and constructors aren't allowed except for in `debug_utils.hpp`.
-14. `debug_utils.hpp` must never be included.
-15. Assumptions on the user's behalf aren't allowed. For example, the implementation shouldn't adjust config values silently or with a warning; it should throw an exception instead.
-16. Samples:
+8. Follow constructors and member initializer lists style instead of direct assignments in the constructor body.
+9. When initial container values are known upfront, prefer initializer-list / brace-initialization over constructing an empty container and immediately inserting values.
+10. Make sure the function names are descriptive.
+11. Check for variables with different names but similar meaning or aliasing.
+12. Avoid duplicate code. Ensure that common functionality is extracted into reusable functions or utilities.
+13. Avoid pronouns in comments and names to make the statements concise.
+14. Unused functions and constructors aren't allowed except for in `debug_utils.hpp`.
+15. `debug_utils.hpp` must never be included.
+16. Assumptions on the user's behalf aren't allowed. For example, the implementation shouldn't adjust config values silently or with a warning; it should throw an exception instead.
+17. Extend sample and functional tests with `tiny-random` model when a new model architecture is added.
+18. When factoring out a function, ensure the implementation doesn't change.
+19. Samples:
     - Avoid adding new samples unless there is a strong, clearly justified reason.
     - Keep command‑line arguments in samples minimal. Prefer hardcoding values.
     - Ensure new samples have corresponding tests.
@@ -55,3 +58,4 @@ When performing a code review on a Pull Request, additionally follow this protoc
 6. Documentation: ensure that any new public APIs have docstrings in C++ headers and Python bindings. Ensure that new public APIs have documentation updated in /site.
 7. Test Coverage: ensure that new features or changes have corresponding tests.
 8. Verify that the result of every newly introduced function is used in at least one call site except for `void` functions.
+9. Helper scripts shouldn't be committed.
PATCH

echo "Gold patch applied."
