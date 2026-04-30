# chore: optimise `.claude/CLAUDE.md`

Source: [dfinity/ic#8994](https://github.com/dfinity/ic/pull/8994)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/CLAUDE.md`

## What to add / change

* Claude Opus 4.6 did not always immediately use the correct `cargo fmt` command. It would always figure it out on the 2nd try but to not waste tokens this instructs the AI to use the right command directly.

* Also remove the paragraph about system-tests since that made Claude hesitant to run system-tests. Just instruct to always run `bazel test`.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
