# Added AGENTS.md to Shade

Source: [TryGhost/Ghost#24864](https://github.com/TryGhost/Ghost/pull/24864)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `apps/shade/AGENTS.md`

## What to add / change

ref https://linear.app/ghost/issue/PROD-2615/add-agentsmd-to-shade

- As part of an experiment I've added a global AGENTS.md file to Shade that contains guidlines (mostly) for AI coding agents.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
