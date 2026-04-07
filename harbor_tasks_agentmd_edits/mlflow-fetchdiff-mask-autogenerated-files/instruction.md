# fetch-diff: Show auto-generated files with masked diff instead of excluding them

## Problem

The `fetch-diff` skill currently excludes auto-generated files (protobuf output, lock files) entirely from the diff output. This means reviewers have no visibility into whether these files changed at all. Additionally, `.ipynb` notebook files are incorrectly treated as auto-generated and excluded.

The current function `should_exclude_file` removes these files from the output completely, which loses useful signal — knowing that a lock file changed is valuable even if the actual content diff is noise.

## Expected Behavior

Auto-generated files should still appear in the diff output, but with their hunk content replaced by a mask message (e.g., `[Auto-generated file - diff masked]`). The diff headers (`diff --git`, `---`, `+++`) should be preserved so reviewers can see which auto-generated files were touched. The mask message should appear only once per file, even if the file has multiple hunks.

Notebook files (`.ipynb`) should no longer be treated as auto-generated — they should appear with their full diff content.

After making the code changes, update the skill's documentation (SKILL.md) to reflect the new behavior — the description and output examples should accurately describe how auto-generated files are handled now.

## Files to Look At

- `.claude/skills/src/skills/commands/fetch_diff.py` — the diff filtering logic
- `.claude/skills/fetch-diff/SKILL.md` — skill documentation that describes the behavior
