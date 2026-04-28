# Create AGENTS.md

Source: [bigcommerce/catalyst#2561](https://github.com/bigcommerce/catalyst/pull/2561)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `core/AGENTS.md`

## What to add / change

## What/Why?
Add an [AGENTS.md](https://agents.md/) file to help AI-assisted development tools in understand the structure of Catalyst as well as the best practices for extending it.

## Testing
TBD - need to test various development scenarios

## Migration
N/A

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
