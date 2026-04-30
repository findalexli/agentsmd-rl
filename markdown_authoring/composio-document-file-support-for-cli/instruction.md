# Document `--file` support for CLI skill uploads

Source: [ComposioHQ/composio#3114](https://github.com/ComposioHQ/composio/pull/3114)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `ts/packages/cli/skills/composio-cli/SKILL.md`

## What to add / change

## Summary
- Documented how to upload a local file with `composio execute` when a tool exposes a single `file_uploadable` input.
- Added an example for `SLACK_UPLOAD_OR_CREATE_A_FILE_IN_SLACK` using `--file` alongside `-d` JSON arguments.
- Clarified that `--file` only applies when there is exactly one uploadable file field; otherwise `-d` JSON should be used.

## Testing
- Not run (documentation-only change).
- Verified the updated CLI skill guidance in `ts/packages/cli/skills/composio-cli/SKILL.md`.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
