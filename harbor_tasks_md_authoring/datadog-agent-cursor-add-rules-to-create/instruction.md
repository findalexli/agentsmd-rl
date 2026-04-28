# cursor: Add rules to create an agent core check

Source: [DataDog/datadog-agent#42223](https://github.com/DataDog/datadog-agent/pull/42223)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/agent_corecheck.mdc`

## What to add / change

### What does this PR do?

This PR adds a .mdc rules file to teach AI agents to create core checks.

### Motivation

Make development of new checks easier, also acts as documentation for humans.

### Describe how you validated your changes

Docs-only change.

### Additional Notes

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
