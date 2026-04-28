# fix: correct misleading FileNotFoundError message in example

Source: [Tracer-Cloud/opensre#1004](https://github.com/Tracer-Cloud/opensre/pull/1004)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `tests/AGENTS.md`

## What to add / change

## Summary

Fixed the misleading `FileNotFoundError` message in the example code. Changed "empty file not present" to "input file not present" to correctly match the `os.path.exists()` condition being checked.

## Related

Closes #828

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
