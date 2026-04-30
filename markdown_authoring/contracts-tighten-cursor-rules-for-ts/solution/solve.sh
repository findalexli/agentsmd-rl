#!/usr/bin/env bash
set -euo pipefail

cd /workspace/contracts

# Idempotency guard
if grep -qF "- **Linting**: Run the relevant linter on **all files you created or edited** (e" ".cursor/rules/099-finish.mdc" && grep -qF "- When editing any file matching this rule\u2019s globs, run `bunx eslint <file(s)>` " ".cursor/rules/200-typescript.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/099-finish.mdc b/.cursor/rules/099-finish.mdc
@@ -6,6 +6,9 @@ globs:
 alwaysApply: true
 ---
 
+**Scope**: This checklist applies to **every file you create or modify** during the task, including files you added or edited that were not mentioned in the user’s initial prompt. Before finalizing, run the relevant checks on all such files.
+
 - **Conventions**: Verify `[CONV:LICENSE]`/`[CONV:NATSPEC]`/`[CONV:BLANKLINES]`/`[CONV:NAMING]` satisfied; avoid interface/storage changes unless requested.
 - **Testing**: After Solidity changes → `forge test` (or note suites remaining); after TS → lint/tests with Bun; after Bash → check execution flags/sourcing. State explicitly if anything not run.
+- **Linting**: Run the relevant linter on **all files you created or edited** (e.g. `bunx eslint` for TS/JS, or the project’s lint command) and fix all reported issues before finalizing. Do not claim the code is free of lint errors unless the linter has been run on those files and exited successfully.
 - **Summary format**: Start with applied rules (filename/anchor), include tests/lints run, call out follow-ups/gaps.
diff --git a/.cursor/rules/200-typescript.mdc b/.cursor/rules/200-typescript.mdc
@@ -15,6 +15,7 @@ globs:
 ## Code Quality
 
 - Obey `.eslintrc.cjs`; avoid `any`; use TypeChain types from `typechain/` directory (e.g., `ILiFi.BridgeDataStruct`).
+- When editing any file matching this rule’s globs, run `bunx eslint <file(s)>` and fix all reported issues before finalizing; do not introduce new lint violations.
 - **Always reuse existing helpers and types**: Search `script/common/`, `script/utils/`, `script/demoScripts/utils/`, and other helper directories before implementing new functionality. Key helpers:
   - `script/utils/deploymentHelpers.ts` (deployment loading),
   - `script/demoScripts/utils/demoScriptHelpers.ts` (viem-based demo helpers and swap helpers),
PATCH

echo "Gold patch applied."
