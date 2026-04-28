# Add dda install in AGENTS.md

Source: [DataDog/datadog-agent#40346](https://github.com/DataDog/datadog-agent/pull/40346)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

This is just a template. Please delete all unneeded sections and add others if appropriate.

### What does this PR do?
Add dda install instruction in AGENTS.md.

### Motivation

### Describe how you validated your changes (if not by through tests)

### Possible Drawbacks / Trade-offs

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
