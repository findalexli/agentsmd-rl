#!/usr/bin/env bash
set -euo pipefail

cd /workspace/codeflash

# Idempotency guard
if grep -qF "- **Docstrings**: Do not add docstrings to new or changed code unless the user e" ".claude/rules/code-style.md" && grep -qF "- Don't commit intermediate states \u2014 wait until the full implementation is compl" ".claude/rules/git.md" && grep -qF "- Use pytest's `tmp_path` fixture for temp directories \u2014 do not use `tempfile.mk" ".claude/rules/testing.md" && grep -qF "3. Spawn subagents (using the Agent tool) to attempt the fix \u2014 each subagent sho" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/rules/code-style.md b/.claude/rules/code-style.md
@@ -5,9 +5,11 @@
 - **Package management**: Always use `uv`, never `pip`
 - **Tooling**: Ruff for linting/formatting, mypy strict mode, prek for pre-commit checks
 - **Comments**: Minimal - only explain "why", not "what"
-- **Docstrings**: Do not add unless explicitly requested
+- **Docstrings**: Do not add docstrings to new or changed code unless the user explicitly asks for them — not even one-liners. The codebase intentionally keeps functions self-documenting through clear naming and type annotations
+- **Types**: Match the type annotation style of surrounding code — the codebase uses annotations, so add them in new code
 - **Naming**: NEVER use leading underscores (`_function_name`) - Python has no true private functions, use public names
 - **Paths**: Always use absolute paths
 - **Encoding**: Always pass `encoding="utf-8"` to `open()`, `read_text()`, `write_text()`, etc. in new or changed code — Windows defaults to `cp1252` which breaks on non-ASCII content. Don't flag pre-existing code that lacks it unless you're already modifying that line.
+- **Verification**: Use `uv run prek` to verify code — it handles ruff, ty, mypy in one pass. Don't run `ruff`, `mypy`, or `python -c "import ..."` separately; `prek` is the single verification command
 - **Pre-commit**: Run `uv run prek` before committing — fix any issues before creating the commit
 - **Pre-push**: Before pushing, run `uv run prek run --from-ref origin/<base>` to check all changed files against the PR base — this matches CI behavior and catches issues that per-commit prek misses. To detect the base branch: `gh pr view --json baseRefName -q .baseRefName 2>/dev/null || echo main`
diff --git a/.claude/rules/git.md b/.claude/rules/git.md
@@ -1,7 +1,17 @@
 # Git Commits & Pull Requests
 
-- **Always create a new branch from `main` before starting any new work** — never commit directly to `main` or reuse an existing feature branch for unrelated changes
+## Commits
+- Never commit, amend, or push without explicit permission
+- Don't commit intermediate states — wait until the full implementation is complete, reviewed, and explicitly approved before committing. If the user corrects direction mid-implementation, incorporate the correction before any commit
+- Always create a new branch from `main` before starting any new work — never commit directly to `main` or reuse an existing feature branch for unrelated changes
 - Use conventional commit format: `fix:`, `feat:`, `refactor:`, `docs:`, `test:`, `chore:`
 - Keep commits atomic - one logical change per commit
 - Commit message body should be concise (1-2 sentences max)
-- PR titles should also use conventional format
+- Merge for simple syncs, rebase when branches have diverged significantly
+- When committing to an external/third-party repo, follow that repo's own conventions for versioning, changelog, and CI
+
+## Pull Requests
+- PR titles should use conventional format
+- Keep the PR body short and straight to the point
+- If related to a Linear issue, include `CF-#` in the body
+- Branch naming: `cf-#-title` (lowercase, hyphenated), no other prefixes/suffixes
diff --git a/.claude/rules/testing.md b/.claude/rules/testing.md
@@ -7,9 +7,8 @@ paths:
 # Testing Conventions
 
 - Code context extraction and replacement tests must always assert for full string equality, no substring matching.
-- Use pytest's `tmp_path` fixture for temp directories (it's a `Path` object).
-- Write temp files inside `tmp_path`, never use `NamedTemporaryFile` (causes Windows file contention).
-- Always call `.resolve()` on Path objects to ensure absolute paths and resolve symlinks.
+- Use pytest's `tmp_path` fixture for temp directories — do not use `tempfile.mkdtemp()`, `tempfile.TemporaryDirectory()`, or `NamedTemporaryFile`. Some existing tests still use `tempfile` but new tests must use `tmp_path`.
+- Always call `.resolve()` on Path objects before passing them to functions under test — this ensures absolute paths and resolves symlinks. Example: `source_file = (tmp_path / "example.py").resolve()`
 - Use `.as_posix()` when converting resolved paths to strings (normalizes to forward slashes).
 - Any new feature or bug fix that can be tested automatically must have test cases.
 - If changes affect existing test expectations, update the tests accordingly. Tests must always pass after changes.
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -19,7 +19,12 @@ Discovery → Ranking → Context Extraction → Test Gen + Optimization → Bas
 7. **Result** (`result/`, `github/`): Create PR with winning optimization
 
 # Instructions
-- When I report a bug, don't start by trying to fix it. Instead, start by writing a test that reproduces the bug. Then, have subagents try to fix the bug and prove it with a passing test.
+- **Bug fix workflow** — follow these steps in order, do not skip ahead:
+  1. Read the relevant code to understand the bug
+  2. Write a test that reproduces the bug (run it to confirm it fails)
+  3. Spawn subagents (using the Agent tool) to attempt the fix — each subagent should apply a fix and run the test to prove it passes
+  4. Review the subagent results, pick the best fix, and apply it
+  5. Never jump straight to writing a fix yourself — always go through steps 1-4
 - Everything that can be tested should have tests.
 
 <!-- Section below is auto-generated by `tessl install` - do not edit manually -->
PATCH

echo "Gold patch applied."
