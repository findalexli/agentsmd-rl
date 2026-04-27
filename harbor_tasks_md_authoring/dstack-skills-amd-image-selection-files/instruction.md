# [Skills] AMD image selection, `files`, `repos`, `image` guidance

Source: [dstackai/dstack#3634](https://github.com/dstackai/dstack/pull/3634)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/dstack/SKILL.md`

## What to add / change

Primary:
- [x] Clarifies `image` selection guidance in `skills/dstack/SKILL.md`, including default ROCm image recommendations (`rocm/*`) for AMD runs

Minor:
- [x] Note that `python` and `image` are mutually exclusive
- [x] Additional guidance around `files` and `repos` regarding `working_dir`

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
