# Creates copilot-instructions.md

Source: [habitat-sh/habitat#9930](https://github.com/habitat-sh/habitat/pull/9930)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Creates a copilot-instructions.md.

Notes and Caveats:
- Updated the "NEVER MODIFY THESE FILES" after the initial generation
- Part of the repository structure might be able to updated. I think the directories skipped might be plan files which Copilot isn't ready to deal with yet though.
- `cargo tarpaulin` is used but that isn't installed by default so that will break.
  - Also, I think maybe cargo-llvm-cov might be a better tool
- The default clippy and rustfmt commands probably won't work well as is as I wouldn't expect them to have our customizations.  I think maybe we should sub our make targets.
- ???

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
