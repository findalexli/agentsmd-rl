#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "- **Type selection \u2014 classify by intent, not diff shape.** Where `fix:` and `fea" "AGENTS.md" && grep -qF "When using conventional commits, choose the type that most precisely describes t" "plugins/compound-engineering/skills/ce-commit-push-pr/SKILL.md" && grep -qF "When using conventional commits, choose the type that most precisely describes t" "plugins/compound-engineering/skills/ce-commit/SKILL.md" && grep -qF "- If the current branch is the default branch, ask whether to create a feature b" "plugins/compound-engineering/skills/ce-debug/SKILL.md" && grep -qF "- **Type** is chosen by intent, not file extension or diff shape. `feat` for new" "plugins/compound-engineering/skills/ce-pr-description/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -93,8 +93,9 @@ cat plugins/compound-engineering/.claude-plugin/plugin.json | jq .
 ## Commit Conventions
 
 - **Prefix is based on intent, not file type.** Use conventional prefixes (`feat:`, `fix:`, `docs:`, `refactor:`, etc.) but classify by what the change does, not the file extension. Files under `plugins/*/skills/`, `plugins/*/agents/`, and `.claude-plugin/` are product code even though they are Markdown or JSON. Reserve `docs:` for files whose sole purpose is documentation (`README.md`, `docs/`, `CHANGELOG.md`).
+- **Type selection — classify by intent, not diff shape.** Where `fix:` and `feat:` could both seem to fit, default to `fix:`: a change that remedies broken or missing behavior is `fix:` even when implemented by adding code, and net additions do not turn a fix into a `feat:`. Reserve `feat:` for capabilities the user could not previously accomplish where nothing was broken. Other conventional types (`chore:`, `refactor:`, `docs:`, `perf:`, `test:`, `ci:`, `build:`, `style:`) remain primary when they describe the change more precisely than either. Heuristic: if a regression test you could write today would have failed *before* the change, it's `fix:`. The user may override this default for a specific change.
 - **Include a component scope.** The scope appears verbatim in the changelog. Pick the narrowest useful label: skill/agent name (`document-review`, `learnings-researcher`), plugin or CLI area (`coding-tutor`, `cli`), or shared area when cross-cutting (`review`, `research`, `converters`). Never use `compound-engineering` — it's the entire plugin and tells the reader nothing. Omit scope only when no single label adds clarity.
-- Breaking changes must be explicit with `!` or a breaking-change footer so release automation can classify them correctly.
+- **Never use `!` or a `BREAKING CHANGE:` footer without explicit user confirmation.** These markers trigger release-please's automatic major version bump — a decision the user may not want even when a change is technically breaking. If a change appears breaking, surface that to the user and let them decide whether to apply the marker.
 
 ## Adding a New Target Provider
 
diff --git a/plugins/compound-engineering/skills/ce-commit-push-pr/SKILL.md b/plugins/compound-engineering/skills/ce-commit-push-pr/SKILL.md
@@ -133,6 +133,8 @@ Priority order for commit messages and PR titles:
 2. **Recent commit history** -- match the pattern in the last 10 commits.
 3. **Default** -- `type(scope): description` (conventional commits).
 
+When using conventional commits, choose the type that most precisely describes the change. Where `fix:` and `feat:` both seem to fit, default to `fix:`: a change that remedies broken or missing behavior is `fix:` even when implemented by adding code. Reserve `feat:` for capabilities the user could not previously accomplish. Other types (`chore:`, `refactor:`, `docs:`, `perf:`, `test:`, `ci:`, `build:`, `style:`) remain primary when they fit better. The user may override for a specific change.
+
 ### Step 3: Check for existing PR
 
 Use the current branch and existing PR check from context. If the branch is empty, report detached HEAD and stop.
diff --git a/plugins/compound-engineering/skills/ce-commit/SKILL.md b/plugins/compound-engineering/skills/ce-commit/SKILL.md
@@ -69,6 +69,8 @@ Follow this priority order:
 2. **Recent commit history** -- If no explicit convention is documented, examine the 10 most recent commits from Step 1. If a clear pattern emerges (e.g., conventional commits, ticket prefixes, emoji prefixes), match that pattern.
 3. **Default: conventional commits** -- If neither source provides a pattern, use conventional commit format: `type(scope): description` where type is one of `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`, `ci`, `style`, `build`.
 
+When using conventional commits, choose the type that most precisely describes the change (the type list above). Where `fix:` and `feat:` both seem to fit, default to `fix:`: a change that remedies broken or missing behavior is `fix:` even when implemented by adding code. Reserve `feat:` for capabilities the user could not previously accomplish. Other types remain primary when they fit better. The user may override for a specific change.
+
 ### Step 3: Consider logical commits
 
 Before staging everything together, scan the changed files for naturally distinct concerns. If modified files clearly group into separate logical changes (e.g., a refactor in one directory and a new feature in another, or test files for a different change than source files), create separate commits for each group.
diff --git a/plugins/compound-engineering/skills/ce-debug/SKILL.md b/plugins/compound-engineering/skills/ce-debug/SKILL.md
@@ -169,7 +169,10 @@ Present the diagnosis to the user before proceeding.
 
 If the user chose "Diagnosis only" at the end of Phase 2, skip this phase and go straight to Phase 4 for the summary — the skill's job was the diagnosis. If they chose "Rethink the design", control has transferred to `/ce-brainstorm` and this skill ends.
 
-**Workspace check:** Before editing files, check for uncommitted changes (`git status`). If the user has unstaged work in files that need modification, confirm before editing — do not overwrite in-progress changes.
+**Workspace and branch check:** Before editing files:
+
+- Check for uncommitted changes (`git status`). If the user has unstaged work in files that need modification, confirm before editing — do not overwrite in-progress changes.
+- If the current branch is the default branch, ask whether to create a feature branch first using the platform's blocking question tool (see Phase 2 for the per-platform names). To detect the default branch, compare against `main`, `master`, or the value of `git rev-parse --abbrev-ref origin/HEAD` with its `origin/` prefix stripped (the raw output is `origin/<name>`, so an unstripped comparison will never match the local branch name). Default to creating one; derive a name from the bug and run `git checkout -b <name>`. On any other branch, proceed.
 
 **Test-first:**
 1. Write a failing test that captures the bug (or use the existing failing test)
@@ -207,6 +210,9 @@ How was this introduced? What allowed it to survive? If a systemic gap was found
 
 Options (include only those that apply):
 
-1. **Commit the fix** — stage and commit the change (always applies here, since Phase 3 ran)
-2. **Document as a learning** (`/ce-compound`) — capture the bug and fix as a reusable pattern
-3. **Post findings to the issue** — reply on the tracker with confirmed root cause, verified reproduction, relevant code references, and suggested fix direction (include only when entry came from an issue tracker)
+1. **Commit the fix (`/ce-commit`)** — stage and commit the change locally (always applies here, since Phase 3 ran)
+2. **Commit and open a PR (`/ce-commit-push-pr`)** — commit, push, and open a pull request
+3. **Document as a learning first (`/ce-compound`)** — capture the bug and fix as a reusable pattern
+4. **Post findings to the issue first** — reply on the tracker with confirmed root cause, verified reproduction, relevant code references, and suggested fix direction (include only when entry came from an issue tracker)
+
+Options 1 and 2 are terminal — running either ends the skill. Options 3 and 4 are additive: after the chosen action completes, re-prompt with the remaining options (excluding the one just completed and any that no longer apply).
diff --git a/plugins/compound-engineering/skills/ce-pr-description/SKILL.md b/plugins/compound-engineering/skills/ce-pr-description/SKILL.md
@@ -306,7 +306,7 @@ If a `focus:` hint was provided, incorporate it alongside the diff-derived narra
 
 Title format: `type: description` or `type(scope): description`.
 
-- **Type** is chosen by intent, not file extension. `feat` for new functionality, `fix` for a bug fix, `refactor` for a behavior-preserving change, `docs` for doc-only, `chore` for tooling/maintenance, `perf` for performance, `test` for test-only.
+- **Type** is chosen by intent, not file extension or diff shape. `feat` for new functionality, `fix` for a bug fix, `refactor` for a behavior-preserving change, `docs` for doc-only, `chore` for tooling/maintenance, `perf` for performance, `test` for test-only. Where `fix` and `feat` could both seem to fit, default to `fix`: a change that remedies broken or missing behavior is `fix` even when implemented by adding code. Reserve `feat` for capabilities the user could not previously accomplish. The user may override.
 - **Scope** (optional) is the narrowest useful label: a skill/agent name, CLI area, or shared area. Omit when no single label adds clarity.
 - **Description** is imperative, lowercase, under 72 characters total. No trailing period.
 - If the repo has commit-title conventions visible in recent commits, match them.
PATCH

echo "Gold patch applied."
