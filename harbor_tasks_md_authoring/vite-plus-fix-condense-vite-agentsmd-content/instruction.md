# fix: Condense Vite+ `AGENTS.md` content.

Source: [voidzero-dev/vite-plus#1430](https://github.com/voidzero-dev/vite-plus/pull/1430)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `packages/cli/AGENTS.md`

## What to add / change

This PR condenses the contents of what we write to `AGENTS.md` to a minimum. The long version was previously necessary to steer models because Vite+ is not in the training set. Now that Vite+ is released, and the docs are available, we can condense the content we inject to a more narrow set of instructions which saves tokens.

In the future we might be able to reduce this even further, but I keep noticing that without explicit instructions, agents tend to forget to run things like `vp check` or `vp test` because they are not explicitly defined in the project compared to when using package managers directly.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
