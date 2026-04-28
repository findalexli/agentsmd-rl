# Explain SASS diffs in `AGENTS.md`

Source: [NVIDIA/cccl#7733](https://github.com/NVIDIA/cccl/pull/7733)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

I used this a few times now to successfully ask Cursor to find the cause of SASS differences and fix them. I have no idea what good practices are for how to describe such stuff in AGENTS.md, so please let me know if this can be improved in any way.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
