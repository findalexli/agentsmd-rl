#!/usr/bin/env bash
set -euo pipefail

cd /workspace/openvino.genai

# Idempotency guard
if grep -qF "1. PR description must be aligned with [./pull_request_template.md](./pull_reque" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -16,29 +16,31 @@ You are the OpenVINO GenAI Reviewer. Your mission is to ensure that all new code
 
 ## Code Review Instructions for PRs
 When analyzing a Pull Request, follow this protocol:
-1. Follow C++ Core Guidelines strictly. Include references in your comments.
-2. Check for 'Hidden' Performance Tax: Look for dynamic_cast in the hot path (inference loops). Suggest static_cast or redesigning if the type is known.
-3. Avoid copies: Ensure that large data structures (like tensors) are passed by reference or moved, not copied.
-4. Python Bindings: If C++ APIs are changed, check if the corresponding Python pybind11 wrappers in src/python need updates.
-5. Exceptions: Use OPENVINO_ASSERT(condition, ...) for checks instead of if + throw.
-6. Documentation: Ensure that any new public APIs have docstrings in C++ headers and Python bindings. Ensure that new public APIs have documentation updated in /site.
-7. Test Coverage: Ensure that new features or changes have corresponding tests.
-8. Formatting & Safety:
+1. PR description must be aligned with [./pull_request_template.md](./pull_request_template.md) and its checklist must be filled out. If not, request the author to update the description and checklist before proceeding with the review.
+2. PR description must be up to date and include all information about the changes.
+3. Follow C++ Core Guidelines strictly. Include references in your comments.
+4. Check for 'Hidden' Performance Tax: Look for dynamic_cast in the hot path (inference loops). Suggest static_cast or redesigning if the type is known.
+5. Avoid copies: Ensure that large data structures (like tensors) are passed by reference or moved, not copied.
+6. Python Bindings: If C++ APIs are changed, check if the corresponding Python pybind11 wrappers in src/python need updates.
+7. Exceptions: Use OPENVINO_ASSERT(condition, ...) for checks instead of if + throw.
+8. Documentation: Ensure that any new public APIs have docstrings in C++ headers and Python bindings. Ensure that new public APIs have documentation updated in /site.
+9. Test Coverage: Ensure that new features or changes have corresponding tests.
+10. Formatting & Safety:
     * No `using namespace std;`.
     * No `auto` for primitive types where it obscures readability.
     * Use `const` and `constexpr` wherever possible.
-9. Pass non-fundamental values by `const` reference wherever possible.
-10. Follow constructors and member initializer lists style instead of direct assignments in the constructor body.
-11. Verify that the result of every newly introduced function is used in at least one call site except for `void` functions.
-12. Make sure the function names are descriptive.
-13. Check for variables with different names but similar meaning or aliasing.
-14. Avoid duplicate code. Ensure that common functionality is extracted into reusable functions or utilities.
-15. When initial container values are known upfront, prefer initializer-list / brace-initialization over constructing an empty container and immediately inserting values.
-16. Avoid pronouns in comments and names to make the statements concise.
-17. Unused functions and constructors aren't allowed except for in `debug_utils.hpp`.
-18. `debug_utils.hpp` must never be included.
-19. Assumptions on the user's behalf aren't allowed. For example, the implementation shouldn't adjust config values silently or with a warning; it should throw an exception instead.
-20. Samples:
+11. Pass non-fundamental values by `const` reference wherever possible.
+12. Follow constructors and member initializer lists style instead of direct assignments in the constructor body.
+13. Verify that the result of every newly introduced function is used in at least one call site except for `void` functions.
+14. Make sure the function names are descriptive.
+15. Check for variables with different names but similar meaning or aliasing.
+16. Avoid duplicate code. Ensure that common functionality is extracted into reusable functions or utilities.
+17. When initial container values are known upfront, prefer initializer-list / brace-initialization over constructing an empty container and immediately inserting values.
+18. Avoid pronouns in comments and names to make the statements concise.
+19. Unused functions and constructors aren't allowed except for in `debug_utils.hpp`.
+20. `debug_utils.hpp` must never be included.
+21. Assumptions on the user's behalf aren't allowed. For example, the implementation shouldn't adjust config values silently or with a warning; it should throw an exception instead.
+22. Samples:
     * Avoid adding new samples unless there is a strong, clearly justified reason.
     * Keep command‑line arguments in samples minimal.
     * Ensure new samples have corresponding tests.
PATCH

echo "Gold patch applied."
