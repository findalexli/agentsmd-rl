#!/usr/bin/env bash
set -euo pipefail

cd /workspace/harness-engineering

# Idempotency guard
if grep -qF "- **Two sets of generate-docs**: `scripts/repo-generate-docs.js` is this repo's " "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -18,7 +18,7 @@ This file provides guidance to Claude Code when working with code in this reposi
 
 ### Testing
 ```bash
-node --experimental-vm-modules node_modules/.bin/jest tests/scripts/   # Unit tests for setup scripts
+npx jest --config '{}' tests/scripts/                                  # Unit tests for setup scripts
 bash tests/evals/run-evals.sh                                          # E2E readiness evals (default)
 bash tests/evals/run-evals.sh --config setup-eval-config.json          # E2E setup evals
 bash tests/evals/test-marketplace-install.sh                           # Test plugin install flow
@@ -165,10 +165,12 @@ User runs /setup
 Before merging:
 - [ ] No files over 300 lines (run `find . -name "*.js" -not -path "*/node_modules/*" -exec wc -l {} + | awk '$1 > 300'`)
 - [ ] No hardcoded secrets (run `node skills/setup/scripts/lib/check-secrets.js`)
-- [ ] Tests pass: `node --experimental-vm-modules node_modules/.bin/jest tests/scripts/`
+- [ ] Tests pass: `npx jest --config '{}' tests/scripts/`
 - [ ] Doc validation passes: `node skills/setup/scripts/lib/validate-docs.js --full`
-- [ ] CLAUDE.md updated if files were added, removed, or renamed
+- [ ] CLAUDE.md auto-updated by commit hook — verify result looks correct
 - [ ] Critical Gotchas section updated if non-obvious behavior was discovered
+- [ ] If SKILL.md changed, eval config and grader updated in the same PR
+- [ ] Eval dry-run passes after eval infrastructure changes: `bash tests/evals/run-evals.sh --config setup-eval-config.json --dry-run`
 
 ---
 
@@ -180,6 +182,10 @@ Before merging:
 - **No package.json at root**: This is a Claude Code plugin, not an npm package. Tests run via direct node/jest/bash invocation.
 - **`globs:` not `paths:`**: Rule files use `globs:` in YAML frontmatter for path scoping. The official docs say `paths:` but `globs:` works more reliably (see Claude Code issue #17204).
 - **Two sets of hooks**: `scripts/hooks/` are this repo's own git hooks (install with `bash scripts/install-hooks.sh`). `skills/setup/scripts/hooks/` are templates shipped to user projects by `/setup`. Don't confuse them.
+- **Two sets of generate-docs**: `scripts/repo-generate-docs.js` is this repo's auto-doc (scans `skills/`, `scripts/`, `tests/`). `skills/setup/scripts/lib/generate-docs.js` is the template installed into user projects (auto-detects source dirs). Fixing one does not fix the other.
+- **Setup has two code paths**: Node/TS uses the "fast path" (scripts do the work). All other stacks use the "adaptive path" (Claude creates files). The eval uses `conversation_must_not_mention` to catch cross-contamination (e.g., Python setup mentioning npm).
+- **Squash merges leave branches dirty**: After squash-merging a PR, the branch still shows unmerged commits. Always create a fresh branch from main for follow-up work — don't reuse the old branch.
+- **CLAUDE.md auto-updates on commit**: The pre-commit hook runs `repo-generate-docs.js` to regenerate AUTO markers. Don't manually edit content between `<!-- AUTO:tree -->` and `<!-- AUTO:modules -->` markers — it will be overwritten.
 
 ---
 
PATCH

echo "Gold patch applied."
