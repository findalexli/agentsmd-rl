# Deleted files silently dropped from fetch-diff output

## Problem

The `fetch-diff` skill silently drops deleted files from its output. When a PR removes a file, the diff for that file has `b/dev/null` as the destination path. The current code does not handle this case, so reviewers never see that a file was deleted.

## Expected Behavior

Deleted files should appear in the diff output with their headers preserved (`diff --git`, `index`, `---`, `+++`) and hunks replaced with the mask message: `[Deleted file - diff masked]`

The `--files` pattern filtering should match against the real filename for deleted files (the path on the `a/` side of the diff header), not the `dev/null` destination.

After fixing the code, update the fetch-diff skill documentation (`.claude/skills/fetch-diff/SKILL.md`) to include an example showing what deleted file output looks like, using the exact string `[Deleted file - diff masked]` for the mask message, consistent with the existing auto-generated file example.

## Files to Look At

- `.claude/skills/src/skills/commands/fetch_diff.py` — the diff processing code
- `.claude/skills/fetch-diff/SKILL.md` — skill documentation with output format examples
