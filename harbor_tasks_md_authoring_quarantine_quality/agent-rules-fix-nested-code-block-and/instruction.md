# Fix nested code block and remove license bloat

Source: [steipete/agent-rules#11](https://github.com/steipete/agent-rules/pull/11)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `docs/swift6-migration.mdc`
- `project-rules/continuous-improvement.mdc`

## What to add / change

## Summary

- **Fix #6**: Changed outer fence from 3 to 4 backticks in `continuous-improvement.mdc` to properly nest code blocks and prevent `@import` parsing issues
- **Fix #3**: Replaced ~200 lines of Apache License full text with a short reference in `swift6-migration.mdc`

## Changes

### continuous-improvement.mdc
The nested markdown example in "Structure Guidelines" section used 3 backticks for both outer and inner fences, causing the inner code blocks to break out of the example.

### swift6-migration.mdc  
The full Apache License 2.0 text (~200 lines) was embedded in the file. Replaced with a 2-line reference linking to the official license.

## Test plan
- [x] Verify nested code block renders correctly in markdown preview
- [x] Verify license reference link works

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
