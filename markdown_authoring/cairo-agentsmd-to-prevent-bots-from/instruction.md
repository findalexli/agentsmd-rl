# AGENTS.md to prevent bots from reading ast.rs

Source: [starkware-libs/cairo#8386](https://github.com/starkware-libs/cairo/pull/8386)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Added a new file `AGENTS.md` with instructions for AI agents to avoid directly reading or grepping the AST implementation file. Instead instruction direct it to look at the code of generator.rs.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
