# Adopt the AGENTS.md standard

Source: [Shopify/ruby-lsp#3955](https://github.com/Shopify/ruby-lsp/pull/3955)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`
- `AGENTS.md`
- `CLAUDE.md`
- `CLAUDE.md`

## What to add / change

And since Claude code is the only one that doesn't follow it, create a symbolic link from CLAUDE.md to AGENTS.md.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
