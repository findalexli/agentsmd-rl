# docs: rename AGENT.md to AGENTS.md

Source: [camunda/camunda#44019](https://github.com/camunda/camunda/pull/44019)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Description
AGENTS.md is now supported by most tools (including copilot, junie)

## Checklist
<!--- Please delete options that are not relevant. Boxes should be checked by reviewer. -->
- [X] Enable backports when necessary (fex. [for bug fixes](https://github.com/camunda/camunda/blob/main/CONTRIBUTING.md#backporting-changes) or [for CI changes](https://camunda.github.io/camunda/ci/#when-to-backport-ci-changes)).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
