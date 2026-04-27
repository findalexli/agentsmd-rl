#!/usr/bin/env bash
set -euo pipefail

cd /workspace/healthcare-agents

# Idempotency guard
if grep -qF "- Do not merge the feature branch into local `main` before opening or merging th" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -6,6 +6,14 @@
 - The simple self-improvement kit lives in `.claude/commands/eval.md`, `eval/rubric.md`, `eval/results.tsv`, and `eval/role-baselines/`.
 - The old Python eval harness has been removed. The active eval path is the simple self-improvement kit above.
 
+## Git Workflow
+
+- Do not push directly to `main`.
+- For requested edits, create a short-lived branch, commit there, push the branch, open a PR, and merge the PR with `gh pr merge`.
+- Do not merge the feature branch into local `main` before opening or merging the PR. That creates duplicate local merge commits and makes `main` appear ahead/behind after GitHub merges the PR.
+- After a PR is merged, run `git fetch origin --prune` and align local `main` to `origin/main` before continuing work.
+- For docs-only or metadata-only changes, the streamlined path is: branch -> commit -> push branch -> `gh pr create` -> `gh pr merge --merge --delete-branch` -> sync local `main`.
+
 ## Self-Improvement Loop
 
 - When asked to run the healthcare self-improvement loop for an agent, first read `.claude/commands/eval.md` and execute that procedure as a normal task, substituting `$ARGUMENTS` with the requested agent slug.
PATCH

echo "Gold patch applied."
