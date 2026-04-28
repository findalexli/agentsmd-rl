# Add `AGENTS.md`

Source: [ai2cm/ace#829](https://github.com/ai2cm/ace/pull/829)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/ace-context.mdc`
- `.cursor/rules/pr-rereview.mdc`
- `.cursor/rules/pr-review.mdc`
- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

Make repo context and rules more concise and move them to `AGENTS.md`.

Changes:
- Deleted `.cursor/` directory.
- Added `CLAUDE.md` pointing to `AGENTS.md`, since Claude Code doesn't yet support `AGENTS.md` directly.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
