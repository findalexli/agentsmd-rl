#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mcp-context-forge

# Idempotency guard
if grep -qF "- `git diff origin/main..HEAD | bob \"Review this diff for correctness, security," ".claude/skills/pr-review/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/pr-review/SKILL.md b/.claude/skills/pr-review/SKILL.md
@@ -1,57 +1,99 @@
 ---
 name: pr-review
-description: Use when a feature branch is ready for code review, needs rebasing onto main, or before creating/updating a pull request. Also use when asked to review changes, check code quality, or verify a branch is merge-ready.
+description: >-
+  Review code changes for quality, security, correctness, and design. Use when
+  a feature branch is ready for review, before creating or updating a pull
+  request, when asked to check code quality, review changes, look at a diff,
+  or verify a branch is merge-ready. Also triggers on phrases like "review my
+  code", "what do you think of these changes", or "is this ready to merge".
 ---
 
 # PR Review
 
-Review all changes between `main` and the current branch HEAD, plus any staged
-and unstaged working-tree changes.
+A review-only skill. **Do not modify any files** — produce a report the author
+uses to make their own changes.
 
-## Setup
+## Gather context
 
-1. **Rebase** — Unless the user says otherwise, fetch `origin` and rebase onto
-   `origin/main`, resolving conflicts. If the branch has Alembic migrations,
-   run `alembic heads` after rebase — if multiple heads exist, update
-   `down_revision` to restore a single linear history.
+1. **Diff** — Collect all changes between `origin/main` and HEAD, plus any
+   staged/unstaged working-tree changes. This is the review scope. Treat
+   all of these changes as a single unit — assume everything will be
+   committed before merge. Do not report on git staging status (uncommitted,
+   unstaged, etc.) as a finding.
 
-2. **Gather context** — If a PR exists (`gh pr view`):
-   - PR description, title, review comments (`gh pr view --comments`)
-   - Linked issues (`gh issue view N`) to understand requirements
-   If no PR exists, review from the diff alone.
+2. **PR metadata** — If a PR exists (`gh pr view`), read the description,
+   review comments (`gh pr view --comments`), and linked issues
+   (`gh issue view N`) to understand requirements and prior feedback.
 
-3. **Read project docs** — Check for `AGENTS.md`, `CONTRIBUTING.md`,
-   `CLAUDE.md`. These are authoritative for test commands, linter config, and
-   conventions — use their commands exactly, not generic substitutes.
+3. **Project conventions** — Read `AGENTS.md`, `CONTRIBUTING.md`, or
+   `CLAUDE.md` if present. These are authoritative for linter commands, test
+   commands, and coding conventions — use their commands exactly.
 
 ## Review checklist
 
-Review the diff in priority order. Fix blocking issues directly when
-straightforward; flag issues that need human judgment.
+Review the diff in priority order. Report all findings for human review.
 
 | # | Category | Severity | Focus |
 |---|----------|----------|-------|
 | 1 | Security | Blocking | Injection, leaked secrets, auth gaps, OWASP top 10 |
 | 2 | Correctness | Blocking | Logic errors, edge cases, mismatch with linked issues |
-| 3 | Test coverage | Blocking | 100% differential coverage — verify changed code has tests |
-| 4 | Linter compliance | Blocking | Run project linters on touched files; resolve all findings |
+| 3 | Test coverage | Blocking | Differential coverage — verify changed code has tests |
+| 4 | Linter compliance | Blocking | Run project linters on touched files; report findings with exact commands |
 | 5 | Performance | High | N+1 queries, unnecessary allocations, bottlenecks |
-| 6 | Code quality | Medium | Redundancy, over-complexity, code smells |
-| 7 | Consistency | Medium | Follow documented conventions; suggest undocumented ones |
-| 8 | Alembic migrations | Conditional | Idempotence, reversibility, cross-DB compat, data safety, `batch_alter_table` for SQLite |
+| 6 | Redundancy | High | Duplicated logic, copy-paste patterns, shared-utility opportunities |
+| 7 | Design | High | Structural quality — see guidance below |
+| 8 | Consistency | Medium | Adherence to documented conventions |
+| 9 | Alembic migrations | Conditional | Idempotence, reversibility, cross-DB compat, `batch_alter_table` for SQLite |
+
+## Design review guidance
+
+### Structure and modularity
+
+- **Single-responsibility violations** — functions or classes doing more than
+  one thing. Name what each responsibility is and suggest how to split.
+- **God functions** — functions with >50 lines of logic or >3 levels of
+  nesting. Identify extraction points.
+- **Long parameter lists** — >5 parameters often indicate a missing config
+  object or dataclass.
+- **Tight coupling** — modules reaching into each other's internals. Suggest
+  interface boundaries.
+- **Deep nesting** — suggest early returns, guard clauses, or extracted helpers.
+
+### Object-oriented design and polymorphism
+
+This codebase tends toward long if/elif/else chains where polymorphic dispatch
+would be cleaner. **Actively look for these opportunities** in changed code and
+in code adjacent to changes:
+
+- **Type-switching conditionals** — e.g., `if transport == "sse": ... elif
+  transport == "websocket": ...`. Suggest an ABC or Protocol with concrete
+  implementations per variant.
+- **Conditional behavior by enum/string** — functions branching on a type field.
+  Suggest the Strategy or Template Method pattern.
+- **Scattered object creation** — conditionals that construct different objects
+  by type. Suggest a factory method or registry pattern.
+- **Dict-dispatch** — for simpler cases where class hierarchies are overkill,
+  `dict[key, callable]` dispatch tables are a good stepping stone.
+- **Copy-paste behavior across classes** — suggest a `Protocol` (structural
+  subtyping) or mixin.
+- **Missing abstract parents** — when classes share an interface but lack a
+  common base, suggest an `ABC` with `@abstractmethod`.
+
+### Missing abstractions
+
+- **Repeated patterns** across 3+ call sites → shared utility or base class.
+- **Data bags with scattered behavior** — pure data classes whose related logic
+  lives in other modules. The behavior should live with the data.
 
 ## Second opinions
 
-After your own review, run available second-opinion tools in parallel as
-background tasks. If a tool is missing from `$PATH` or fails, skip it and note
-reduced coverage.
+After your own review, attempt to run these tools as background tasks. If a
+tool is not installed or fails, skip it and note the reduced coverage.
 
-- **Codex**: `codex exec review --base origin/main`
-- **Bob**: Pipe the diff inline — `git diff origin/main..HEAD | bob "Review this
-  diff for correctness, security, and code quality. Be specific about
-  line-level issues."` Tailor the prompt to the PR content.
+- `codex exec review --base origin/main`
+- `git diff origin/main..HEAD | bob "Review this diff for correctness, security, and design quality. Be specific about line-level issues."`
 
-Attribute findings to their source (Claude/Codex/Bob) and resolve contradictions.
+Attribute findings to their source and resolve contradictions.
 
 ## Output format
 
@@ -62,24 +104,28 @@ Attribute findings to their source (Claude/Codex/Bob) and resolve contradictions
 [1-2 sentence overview: what changed, whether it meets PR/issue goals]
 
 ## Findings
-| # | Severity | Category | File:Line | Issue | Source |
-|---|----------|----------|-----------|-------|--------|
 
-## Fixes Applied
-[Issues fixed directly, with commit refs]
+### Blocking
+| File:Line | Category | Issue | Suggestion |
+|-----------|----------|-------|------------|
 
-## Remaining Issues
-[Issues needing human decision or outside scope]
+### High
+| File:Line | Category | Issue | Suggestion |
+|-----------|----------|-------|------------|
+
+### Medium
+| File:Line | Category | Issue | Suggestion |
+|-----------|----------|-------|------------|
 
 ## Recommendation
-[Pick exactly ONE: "Ready to merge" | "Ready after fixing remaining issues" | "Needs significant rework"]
+[Pick exactly ONE: "Ready to merge" | "Ready after addressing findings" | "Needs significant rework"]
 [1 sentence justification]
 ```
 
 ## Rules
 
-- Never mention Claude, Claude Code, or AI in commits or PR text.
-- Never push unless explicitly asked.
-- Sign commits with `git commit -s`. Verify Git author matches `gh auth status`.
-- Create new commits rather than amending existing ones when rebasing or fixing.
-- After fix-up commits, re-run linters and tests to confirm no regressions.
+- **Do not modify any files.** Report findings for the author to address.
+- Never mention Claude, Claude Code, or AI in any output.
+- Include exact linter commands and output so the author can reproduce.
+- Make suggestions concrete — name the method to extract, the class to create,
+  the interface to define. "Consider refactoring" is not actionable.
PATCH

echo "Gold patch applied."
