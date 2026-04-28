# Update agents.md

Source: [eclipse-rdf4j/rdf4j#5503](https://github.com/eclipse-rdf4j/rdf4j/pull/5503)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

This pull request updates the `AGENTS.md` documentation to clarify version control conventions for the project. The main change is the introduction of specific guidelines for naming branches and formatting commit messages to ensure consistency and traceability.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
