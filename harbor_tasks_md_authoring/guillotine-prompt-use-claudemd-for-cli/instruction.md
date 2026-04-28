# prompt: use CLAUDE.md for cli instructions

Source: [evmts/guillotine#651](https://github.com/evmts/guillotine/pull/651)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`
- `src/cli/CLAUDE.md`

## What to add / change

# Remove CLI development section from main CLAUDE.md and rename CLI guide

### TL;DR

Removed CLI development documentation from main CLAUDE.md and renamed the CLI guide file.

### What changed?

- Removed the "CLI Development" section from the main CLAUDE.md file
- Removed the reference to "guillotine-cli" from the project components list
- Renamed `src/cli/cli.md` to `src/cli/CLAUDE.md` to maintain consistent documentation naming

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
