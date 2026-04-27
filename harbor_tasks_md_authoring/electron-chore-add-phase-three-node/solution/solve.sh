#!/usr/bin/env bash
set -euo pipefail

cd /workspace/electron

# Idempotency guard
if grep -qF "description: Guide for performing Node.js version upgrades in the Electron proje" ".claude/skills/electron-node-upgrade/SKILL.md" && grep -qF "Group related test fixes into a single commit when they address the same root ca" ".claude/skills/electron-node-upgrade/references/phase-three-commit-guidelines.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/electron-node-upgrade/SKILL.md b/.claude/skills/electron-node-upgrade/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: electron-node-upgrade
-description: Guide for performing Node.js version upgrades in the Electron project. Use when working on the roller/node/main branch to fix patch conflicts during `e sync --3`. Covers the patch application workflow, conflict resolution, analyzing upstream Node.js changes, and proper commit formatting for patch fixes.
+description: Guide for performing Node.js version upgrades in the Electron project. Use when working on the roller/node/main branch to fix patch conflicts during `e sync --3`. Covers the patch application workflow, conflict resolution, analyzing upstream Node.js changes, building, running the Node.js test suite, and proper commit formatting for patch fixes.
 ---
 
 # Electron Node.js Upgrade: Phase One
@@ -174,10 +174,127 @@ When the error is in Electron's own source code:
 1. Edit files directly in the electron repo
 2. Commit directly (no patch export needed)
 
+# Electron Node.js Upgrade: Phase Three
+
+## Summary
+
+Run the Node.js test suite via `script/node-spec-runner.js`, fix failing tests, and commit fixes until all tests pass. Certain tests are permanently disabled (listed in `script/node-disabled-tests.json`) and should not be run.
+
+Run Phase Three immediately after Phase Two is complete.
+
+## Success Criteria
+
+Phase Three is complete when:
+- `node script/node-spec-runner.js --default` exits with zero failures
+- All changes are committed per the commit guidelines
+
+Do not stop until these criteria are met.
+
+## Context
+
+Electron runs a subset of Node.js's upstream test suite using a custom runner (`script/node-spec-runner.js`). Tests are executed with the built Electron binary via `ELECTRON_RUN_AS_NODE=true`. Many tests need adaptation because Electron uses BoringSSL (not OpenSSL) and Chromium's V8 (which may differ from Node.js's bundled V8).
+
+**Key files:**
+- `script/node-spec-runner.js` — Test runner script
+- `script/node-disabled-tests.json` — Permanently disabled tests (do not try to fix these)
+- `../third_party/electron_node/test/` — Node.js test files (where patches apply)
+- `patches/node/fix_crypto_tests_to_run_with_bssl.patch` — BoringSSL crypto test adaptations
+- `patches/node/test_formally_mark_some_tests_as_flaky.patch` — Flaky test list
+
+## Workflow
+
+1. Run `node script/node-spec-runner.js --default` from the electron repo
+2. If all tests pass → Phase Three is complete
+3. If tests fail:
+    - Identify the failing test file(s) from the output
+    - Analyze each failure (see "Common Failure Patterns" below)
+    - Fix the test in `../third_party/electron_node/test/...`
+    - Re-run the specific failing test to verify: `node script/node-spec-runner.js {test-path}`
+        - The test path is relative to the node `test/` directory, e.g. `test/parallel/test-crypto-key-objects-raw.js`
+        - Do NOT use `--default` when running specific tests — it adds the full suite flags
+        - Do NOT run tests directly with `ELECTRON_RUN_AS_NODE` — the runner handles environment setup (e.g. temporarily switching `package.json` from ESM to CommonJS)
+    - Commit the fix using the fixup workflow and commit guidelines
+    - Return to step 1
+
+## Commands Reference
+
+| Command | Purpose |
+|---------|---------|
+| `node script/node-spec-runner.js --default` | Run full Node.js test suite |
+| `node script/node-spec-runner.js test/parallel/test-foo.js` | Run a single test |
+| `NODE_REGENERATE_SNAPSHOTS=1 node script/node-spec-runner.js test/test-runner/test-foo.mjs` | Regenerate snapshot for a snapshot-based test |
+
+## Common Failure Patterns
+
+### BoringSSL incompatibilities
+
+Electron uses BoringSSL (via Chromium) instead of OpenSSL. Many crypto features are missing or behave differently:
+
+| Unsupported in BoringSSL | Guard pattern |
+|--------------------------|---------------|
+| ChaCha20-Poly1305 | `if (!process.features.openssl_is_boringssl)` |
+| AES-CCM (aes-128-ccm, aes-256-ccm) | `if (ciphers.includes('aes-128-ccm'))` |
+| AES-KW (key wrapping) | `if (!process.features.openssl_is_boringssl)` |
+| DSA keys | `if (!process.features.openssl_is_boringssl)` |
+| Ed448 / X448 curves | `if (!process.features.openssl_is_boringssl)` |
+| DH key PEM loading | `if (!process.features.openssl_is_boringssl)` |
+| PQC algorithms (ML-KEM, ML-DSA, SLH-DSA) | `if (hasOpenSSL(3, 5))` (already guards these) |
+
+When guarding tests, prefer checking cipher availability (`ciphers.includes(algo)`) over blanket BoringSSL checks where possible, as it's more precise and self-documenting.
+
+New upstream tests that exercise these features will need guards added to the `fix_crypto_tests_to_run_with_bssl` patch.
+
+### Snapshot test mismatches
+
+Some tests compare output against committed `.snapshot` files using `assert.strictEqual` — these are NOT wildcard comparisons. When Chromium's V8 produces different output (e.g. different stack traces due to V8 enhancements), the snapshot must be regenerated:
+
+```bash
+NODE_REGENERATE_SNAPSHOTS=1 node script/node-spec-runner.js test/test-runner/test-foo.mjs
+```
+
+Then inspect the diff to verify the changes are expected, and commit the updated snapshot into the appropriate patch.
+
+### V8 behavioral differences
+
+Chromium's V8 may be ahead of Node.js's bundled V8. This can cause:
+- Different stack trace formats (e.g. thenable async stack frames)
+- Different error messages
+- Features available in Chromium V8 that aren't in stock Node.js V8 (or vice versa)
+
+## Two Types of Test Fixes
+
+### A. Patch Fixes (most common for test failures)
+
+Most test fixes go into existing patches in `patches/node/`. Use the fixup workflow:
+
+1. Edit the test file in `../third_party/electron_node/test/...`
+2. Find the relevant patch commit: `git log --oneline | grep -i "keyword"`
+    - Crypto/BoringSSL tests → `fix crypto tests to run with bssl`
+    - Snapshot tests → the specific snapshot patch (e.g. `test: accomodate V8 thenable`)
+    - Flaky tests → `test: formally mark some tests as flaky`
+3. Create a fixup commit:
+    ```bash
+    cd ../third_party/electron_node
+    git add test/path/to/test.js
+    git commit --fixup=<patch-commit-hash>
+    GIT_SEQUENCE_EDITOR=: git rebase --autosquash --autostash -i <commit>^
+    ```
+4. Export: `e patches node`
+5. **Read `references/phase-three-commit-guidelines.md` NOW**, then commit the updated patch file.
+
+### B. New Patches (rare)
+
+Only create a new patch when the fix doesn't belong in any existing patch. The new patch commit in `../third_party/electron_node` must include a description explaining why the patch exists and when it can be removed — the lint check enforces this.
+
+## Adding to Disabled Tests
+
+Only add a test to `script/node-disabled-tests.json` as a **last resort** — when the test is fundamentally incompatible with Electron's architecture (not just a BoringSSL difference that can be guarded). Tests disabled here are completely skipped and never run.
+
 # Critical: Read Before Committing
 
 - Before ANY Phase One commits: Read `references/phase-one-commit-guidelines.md`
 - Before ANY Phase Two commits: Read `references/phase-two-commit-guidelines.md`
+- Before ANY Phase Three commits: Read `references/phase-three-commit-guidelines.md`
 
 # High-Churn Patches
 
@@ -201,5 +318,6 @@ This skill has additional reference files in `references/`:
 - patch-analysis.md - How to analyze patch failures
 - phase-one-commit-guidelines.md - Commit format for Phase One
 - phase-two-commit-guidelines.md - Commit format for Phase Two
+- phase-three-commit-guidelines.md - Commit format for Phase Three
 
 Read these when referenced in the workflow steps.
diff --git a/.claude/skills/electron-node-upgrade/references/phase-three-commit-guidelines.md b/.claude/skills/electron-node-upgrade/references/phase-three-commit-guidelines.md
@@ -0,0 +1,80 @@
+# Phase Three Commit Guidelines
+
+Only follow these instructions if there are uncommitted changes after fixing a test failure during Phase Three.
+
+Ignore other instructions about making commit messages, our guidelines are CRITICALLY IMPORTANT and must be followed.
+
+## Commit Message Style
+
+**Titles** follow the 60/80-character guideline: simple changes fit within 60 characters, otherwise the limit is 80 characters.
+
+Always include a `Co-Authored-By` trailer identifying the AI model that assisted (e.g., `Co-Authored-By: <AI model attribution>`).
+
+## Commit Types
+
+### Patch updates (most test fixes)
+
+Test fixes go into existing patches via the fixup workflow. Use `fix(patch):` prefix with a descriptive topic:
+
+```
+fix(patch): {topic headline}
+
+Ref: {Node.js commit or issue link}
+
+Co-Authored-By: <AI model attribution>
+```
+
+Examples:
+- `fix(patch): guard DH key test for BoringSSL`
+- `fix(patch): adapt new crypto tests for BoringSSL`
+- `fix(patch): correct thenable snapshot for Chromium V8`
+- `fix(patch): skip AES-KW tests with BoringSSL`
+
+Group related test fixes into a single commit when they address the same root cause (e.g., multiple crypto tests all needing BoringSSL guards for the same missing cipher). Don't create one commit per test file if they share the same fix pattern.
+
+### Snapshot regeneration
+
+When a snapshot test fails because Chromium's V8 produces different output, regenerate it:
+
+```bash
+NODE_REGENERATE_SNAPSHOTS=1 node script/node-spec-runner.js test/test-runner/test-foo.mjs
+```
+
+Then commit the updated snapshot patch with a title describing what changed:
+
+```
+fix(patch): correct {name} snapshot for Chromium V8
+
+Ref: {V8 CL or issue link if known}
+
+Co-Authored-By: <AI model attribution>
+```
+
+### Trivial patch updates
+
+After any patch modification, check for dependent patches that only have index/hunk header changes:
+
+```bash
+git status
+# If other .patch files show as modified with only trivial changes:
+git add patches/
+git commit -m "chore: update patches (trivial only)"
+```
+
+## Finding References
+
+For BoringSSL-related test fixes, the reference is typically the upstream Node.js PR that added the new test:
+
+```bash
+cd ../third_party/electron_node
+git log --oneline -5 -- test/parallel/test-crypto-foo.js
+git log -1 <commit> --format="%B" | grep "PR-URL"
+```
+
+For V8 behavioral differences, reference the Chromium CL:
+
+```
+Ref: https://chromium-review.googlesource.com/c/v8/v8/+/NNNNNNN
+```
+
+If no reference found after searching: `Ref: Unable to locate reference`
PATCH

echo "Gold patch applied."
