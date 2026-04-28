# cursor: Add rules for e2e test development

Source: [DataDog/datadog-agent#43222](https://github.com/DataDog/datadog-agent/pull/43222)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/e2e_tests.mdc`
- `test/new-e2e/tests/gpu/AGENTS.md`

## What to add / change

### What does this PR do?

This PR adds documentation for GPU E2E tests and general E2E test development guidelines. It includes:

1. A new `.cursor/rules/e2e_tests.mdc` file with comprehensive guidelines for working with E2E tests in the datadog-agent repository
2. A new `test/new-e2e/tests/gpu/AGENTS.md` file with specific documentation for GPU E2E tests

### Motivation

Improve developer experience by providing clear documentation for agents to use e2e tests.

### Describe how you validated your changes

N/A

### Additional Notes

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
