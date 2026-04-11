# Deleted files silently dropped from fetch-diff output

## Problem

The `fetch-diff` skill silently drops deleted files from its output. When a PR removes a file, the diff for that file has `b/dev/null` as the destination path. The current `filter_diff()` function in `.claude/skills/src/skills/commands/fetch_diff.py` treats `dev/null` as an exclusion and skips the file entirely, so reviewers never see that a file was deleted.

## Expected Behavior

Deleted files should appear in the diff output with their headers preserved (`diff --git`, `index`, `---`, `+++`) and hunks replaced with a mask message (similar to how auto-generated files are handled). The `--files` pattern filtering should match against the real filename (the `a/` path) for deleted files, not `dev/null`.

After fixing the code, update the fetch-diff skill documentation (`.claude/skills/fetch-diff/SKILL.md`) to include an example showing what deleted file output looks like, consistent with the existing auto-generated file example.

## Files to Look At

- `.claude/skills/src/skills/commands/fetch_diff.py` — the `filter_diff()` function that processes and annotates diff output
- `.claude/skills/fetch-diff/SKILL.md` — skill documentation with output format examples
