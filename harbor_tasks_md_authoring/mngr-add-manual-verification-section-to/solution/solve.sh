#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mngr

# Idempotency guard
if grep -qF "For interactive components (TUIs, interactive prompts, etc.), use `tmux send-key" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -51,8 +51,8 @@ Only after doing all of the above should you begin writing code.
 - Before finishing your response, if you have made any changes, then you must ensure that you have run ALL tests in the project(s) you modified, and that they all pass. DO NOT just run a subset of the tests!
 - Use this command **from the root of the git checkout** to run all tests: "uv run pytest". Never change directories to run tests! Just run the command from the root of the git checkout.
 - Running pytest in this way will produce files in .claude/tests_outputs/ (and tell you about their paths) for things like slow tests and coverage failure.
-- Note that "uv run pytest" defaults to running all "unit" and "integration" tests, but the "acceptance" tests also run in CI. Do *not* run the acceptance tests locally--always allow CI to run them (it's faster than running them locally)
-- If you need to run a specific acceptance test to fix it, iterate on that specific test locally by calling "just test <full_path>::<test_name>" from the root of the git checkout. Do this rather than re-running all tests in CI.
+- Note that "uv run pytest" defaults to running all "unit" and "integration" tests, but the "acceptance" tests also run in CI. Do *not* run the acceptance tests locally to validate changes--always allow CI to run them (it's faster than running them locally).
+- If you need to run a specific acceptance or release test to write or fix it, iterate on that specific test locally by calling "just test <full_path>::<test_name>" from the root of the git checkout. Do this rather than re-running all tests in CI.
 - Note that tasks are *not* be allowed to finish without A) all tests passing in CI, and B) fixing all MAJOR and CRITICAL issues (flagged by a separate reviewer agent).
 - A PR will be made automatically for you when you finish your reply--do NOT create one yourself.
 - **Never change directory**. It's just a good way to get yourself confused.
@@ -66,6 +66,18 @@ Only after doing all of the above should you begin writing code.
 - Do not add TODO or FIXME unless explicitly asked to do so
 - To reiterate: code correctness and quality is the most important concern when writing code.
 
+# Manual verification and testing
+
+Before declaring any feature complete, manually verify it: exercise the feature exactly as a real user would, with real inputs, and critically evaluate whether it *actually does the right thing*. Do not confuse "no errors" with "correct behavior" -- a command that exits 0 but produces wrong output is not working.
+
+Then crystallize the verified behavior into formal tests. Assert on things that are true if and only if the feature worked correctly -- this ensures tests are both reliable and meaningful.
+
+## Verifying interactive components with tmux
+
+For interactive components (TUIs, interactive prompts, etc.), use `tmux send-keys` and `tmux capture-pane` to manually verify them. This is a special case: do NOT crystallize these into pytest tests. They are inherently flaky due to timing and useless in CI, but valuable for agents to verify that interactive behavior looks right during development.
+
+# Git and committing
+
 If desired, the user will explicitly instruct you not to commit.
 
 By default, or if instructed to commit:
PATCH

echo "Gold patch applied."
