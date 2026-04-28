#!/usr/bin/env bash
set -euo pipefail

cd /workspace/redisearch

# Idempotency guard
if grep -qF "6. Do not reference exact line numbers in comments, as they may change over time" ".skills/rust-tests-guidelines/SKILL.md" && grep -qF "Before writing each test, explicitly identify which branch or code path it will " ".skills/write-rust-tests/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.skills/rust-tests-guidelines/SKILL.md b/.skills/rust-tests-guidelines/SKILL.md
@@ -16,6 +16,7 @@ Guidelines for writing new tests for Rust code.
 5. Testing code should be written with the same care reserved to production code.
    Avoid unnecessary duplication, introduce helpers to reduce boilerplate and ensure readability.
    The intent of a test should be obvious or, if not possible, clearly documented.
+6. Do not reference exact line numbers in comments, as they may change over time.
 
 ## Code organization
 
diff --git a/.skills/write-rust-tests/SKILL.md b/.skills/write-rust-tests/SKILL.md
@@ -22,3 +22,14 @@ The generated tests must follow the guidelines outlined in [/rust-tests-guidelin
 
 Ensure that all public APIs are tested thoroughly, including edge cases, error conditions and branches.
 Use [`/check-rust-coverage`](../check-rust-coverage/SKILL.md) to determine which lines are not covered by tests.
+
+## Avoiding redundant tests
+
+Before writing each test, explicitly identify which branch or code path it will cover that no existing test already covers. An uncovered line is not sufficient justification — ask *why* it is uncovered and whether it is reachable through an already-tested entry point.
+
+Two tests are redundant if they exercise the same set of branches in the code under test. Differing only in input values that don't change control flow is not a distinct scenario.
+
+Do not write standalone tests for:
+- **Trivial trait delegations** — `Default`, `From`, or similar trait impls that are single-line delegations to an already-tested constructor, since they will be covered transitively.
+
+After adding tests, double check that every new test covers at least one branch that no other test (existing or new) covers. Remove any that don't.
PATCH

echo "Gold patch applied."
