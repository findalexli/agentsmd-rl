# docs: fix prettier formatting in AGENTS.md

Source: [ChainSafe/lodestar#8930](https://github.com/ChainSafe/lodestar/pull/8930)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Fixes docs CI failure introduced by #8929 — AGENTS.md had code blocks that weren't formatted per Prettier rules.

Run `npx prettier AGENTS.md --write` to fix.

> 🤖 Generated with AI assistance

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
