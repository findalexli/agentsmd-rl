# `CLAUDE.md`: add missing patterns from maintainer review feedback

Source: [vitessio/vitess#19813](https://github.com/vitessio/vitess/pull/19813)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Description

I scraped 9,340 review comments from 18 active Vitess maintainers across 1,970 PRs from the last 4+ years and ran them through Claude Opus 4.6 to identify recurring feedback patterns that aren't captured in `CLAUDE.md`. Only comments from maintainers with merge permissions were considered for a given time frame

The most frequent themes that were missing:

1. **Failure-path safety** — multi-step operations leaving the system half-applied when a later step fails _(~12 comments)_
2. **Conditions broader than intent** — guard clauses that work for known cases but are wider than what's actually meant _(~8 comments)_
3. **`require` vs `assert` in tests** — using `require` when the test can't continue after failure _(~7 comments)_
4. **`t.Context()` over `context.Background()`** — the single most repeated nit _(~8 comments)_
5. **Zero-value / default behaviour safety** — new struct fields silently changing behaviour for existing callers _(~6 comments)_
6. **Context timeout discipline** — unbounded cleanup on `context.Background()`, no timeout while holding locks _(~6 comments)_
7. **Structured logging with `slog`** — explicit push to adopt for new code _(~3 comments)_
8. **MySQL flavour isolation** — version-specific behaviour belongs in the flavour file _(~3 comments)_
9. **User-visible changes need release notes** — even correctness fixes _(~5 comments)_
10. **CI timeout generosity** — 500ms is too low, 30s+ recommended _(~5 comments)_

Also fixed

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
