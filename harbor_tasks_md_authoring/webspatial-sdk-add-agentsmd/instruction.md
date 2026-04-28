# Add AGENTS.md

Source: [webspatial/webspatial-sdk#987](https://github.com/webspatial/webspatial-sdk/pull/987)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary
Add a root-level `AGENTS.md` to help agents and contributors quickly understand the repo layout, common commands, and day-to-day workflows.

## What changed
- Documented repository layout (`packages/*`, `apps/test-server`, `tests/ci-test`, `tools/scripts`).
- Added quick-start commands for install/build/dev/test.
- Captured common workflows (adding a demo page, building packages, running the e2e harness).
- Listed key conventions and pre-commit gotchas (pnpm, lint-staged, file-size and character checks).

## Testing
- `pnpm test`

## Notes
- This PR intentionally only adds documentation and does not change runtime code.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
