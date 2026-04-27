# docs(aflpp): add opinionated environment variables guide

Source: [trailofbits/skills#130](https://github.com/trailofbits/skills/pull/130)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/testing-handbook-skills/skills/aflpp/SKILL.md`

## What to add / change

## Summary

Closes #18

Adds a practical "Environment Variables That Matter" section to the AFL++ skill, based on real-world fuzzing experience. Rather than duplicating the official docs, this provides opinionated guidance on which variables to use and why.

### Sections Added

| Section | Variables | Rationale |
|---------|-----------|-----------|
| **Always Set** | `AFL_TMPDIR`, `AFL_FAST_CAL` | Free performance wins with no downsides |
| **Multi-Core** | `AFL_FINAL_SYNC`, `AFL_TESTCACHE_SIZE` | Prevent missed paths, improve sharing |
| **CI/Automated** | `AFL_EXIT_ON_TIME`, `AFL_EXIT_WHEN_DONE`, `AFL_NO_UI` | Bounded fuzzing for CI pipelines |
| **Avoid** | `AFL_NO_ARITH`, `AFL_SHUFFLE_QUEUE`, `AFL_DISABLE_TRIM` | Usually harmful or unnecessary |

### Placement

Inserted between "Running Campaigns" and "Multi-Core Fuzzing" sections — after the user knows how to run AFL++ but before they scale up.

Follow-up from PR #15 review feedback.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
