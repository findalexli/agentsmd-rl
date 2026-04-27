#!/usr/bin/env bash
set -euo pipefail

cd /workspace/codex

# Idempotency guard
if grep -qF "Do not stop after finding one issue; analyze all possible ways breaking changes " ".codex/skills/code-review-breaking-changes/SKILL.md" && grep -qF "If the change is larger, explain whether it can be split into reviewable stages " ".codex/skills/code-review-change-size/SKILL.md" && grep -qF "5. Highlight new individual items that can cross >1k tokens as P0. These need an" ".codex/skills/code-review-context/SKILL.md" && grep -qF "For agent changes prefer integration tests over unit tests. Integration tests ar" ".codex/skills/code-review-testing/SKILL.md" && grep -qF "Use subagents to review code using all code-review-* skills in this repository o" ".codex/skills/code-review/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.codex/skills/code-review-breaking-changes/SKILL.md b/.codex/skills/code-review-breaking-changes/SKILL.md
@@ -0,0 +1,12 @@
+---
+name: code-breaking-changes
+description: Breaking changes
+---
+
+Search for breaking changes in external integration surfaces:
+- app-server APIs
+- CLI parameters
+- configuration loading
+- resuming sessions from existing rollouts
+
+Do not stop after finding one issue; analyze all possible ways breaking changes can happen.
diff --git a/.codex/skills/code-review-change-size/SKILL.md b/.codex/skills/code-review-change-size/SKILL.md
@@ -0,0 +1,11 @@
+---
+name: code-review-change-size
+description: Change size guidance (800 lines)
+---
+
+Unless the change is mechanical the total number of changed lines should not exceed 800 lines.
+For complex logic changes the size should be under 500 lines.
+
+If the change is larger, explain whether it can be split into reviewable stages and identify the smallest coherent stage to land first.
+Base the staging suggestion on the actual diff, dependencies, and affected call sites.
+
diff --git a/.codex/skills/code-review-context/SKILL.md b/.codex/skills/code-review-context/SKILL.md
@@ -0,0 +1,12 @@
+---
+name: code-review-context
+description: Model visible context
+---
+
+Codex maintains a context (history of messages) that is sent to the model in inference requests.
+
+1. No history rewrite - the context must be built up incrementally.
+2. Avoid frequent changes to context that cause cache misses.
+3. No unbounded items - everything injected in the model context must have a bounded size and a hard cap. 
+4. No items larger than 10K tokens.
+5. Highlight new individual items that can cross >1k tokens as P0. These need an additional manual review.
diff --git a/.codex/skills/code-review-testing/SKILL.md b/.codex/skills/code-review-testing/SKILL.md
@@ -0,0 +1,14 @@
+---
+name: code-review-testing
+description: Test authoring guidance
+---
+
+For agent changes prefer integration tests over unit tests. Integration tests are under `core/suite` and use `test_codex` to set up a test instance of codex.
+
+Features that change the agent logic MUST add an integration test:
+- Provide a list of major logic changes and user-facing behaviors that need to be tested.
+
+If unit tests are needed, put them in a dedicated test file (*_tests.rs).
+Avoid test-only functions in the main implementation.
+
+Check whether there are existing helpers to make tests more streamlined and readable.
diff --git a/.codex/skills/code-review/SKILL.md b/.codex/skills/code-review/SKILL.md
@@ -0,0 +1,14 @@
+---
+name: code-review
+description: Run a final code review on a pull request
+---
+
+Use subagents to review code using all code-review-* skills in this repository other than this orchestrator. One subagent per skill. Pass full skill path to subagents. Use xhigh reasoning.
+
+Make sure to return every single issue. You can return an unlimited number of findings.
+Use raw Markdown to report findings.
+Number findings for ease of reference.
+Each finding must include a specific file path and line number.
+
+If the GitHub user running the review is the owner of the pull request add a `code-reviewed` label.
+Do not leave GitHub comments unless explicitly asked.
PATCH

echo "Gold patch applied."
