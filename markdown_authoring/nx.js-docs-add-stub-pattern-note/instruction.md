# docs: add stub() pattern note to AGENTS.md

Source: [TooTallNate/nx.js#210](https://github.com/TooTallNate/nx.js/pull/210)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Adds a note explaining that `stub()` in TypeScript does NOT mean unimplemented — the C runtime overwrites these methods on prototypes at boot via `NX_DEF_FUNC()`. Only `throw new Error("Method not implemented.")` means actually missing.

This tripped me up while auditing the WebCrypto implementation, so worth documenting for future AI contributors.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
