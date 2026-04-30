# Add `--files` option to fetch-diff skill

## Problem

The `fetch-diff` skill fetches the entire PR diff with no way to scope it to specific files. When reviewing large PRs, developers must sift through unrelated changes to find the files they care about.

## Expected Behavior

The skill should accept an optional `--files` argument that takes one or more fnmatch glob patterns (e.g., `'*.py'`, `'mlflow/server/js/*'`). When provided, only files matching at least one pattern should appear in the output. When omitted, behavior should be unchanged. The existing auto-generated file exclusion (`should_exclude_file`) should still apply on top of any file patterns.

After implementing the code change, update the skill's documentation to reflect the new option with usage examples.

## Files to Look At

- `.claude/skills/src/skills/commands/fetch_diff.py` — the `filter_diff()` and `fetch_diff()` functions, plus `register()` for CLI argument wiring
- `.claude/skills/fetch-diff/SKILL.md` — skill documentation (usage section, examples)
