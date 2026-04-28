# Add AGENTS.md file

Source: [laravel/nightwatch#303](https://github.com/laravel/nightwatch/pull/303)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

This PR introduces a base set of agent guidelines for the project. The guidelines were agent-generated from our existing code, and then further refined until they were able to complete a basic task to an acceptable standard (See #302).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
