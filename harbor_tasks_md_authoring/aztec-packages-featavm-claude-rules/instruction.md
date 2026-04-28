# feat(avm): claude rules

Source: [AztecProtocol/aztec-packages#20101](https://github.com/AztecProtocol/aztec-packages/pull/20101)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `barretenberg/cpp/CLAUDE.md`
- `barretenberg/cpp/pil/vm2/CLAUDE.md`
- `barretenberg/cpp/src/barretenberg/vm2/CLAUDE.md`

## What to add / change

Hey Claude, meet AVM.

I wrote some files, and then asked an agent to make it more concise for LLMs.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
