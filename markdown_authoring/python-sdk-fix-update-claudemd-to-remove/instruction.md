# fix: update CLAUDE.md to remove auto-addition of reviewers.

Source: [modelcontextprotocol/python-sdk#1431](https://github.com/modelcontextprotocol/python-sdk/pull/1431)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

<!-- Provide a brief summary of your changes -->

## Motivation and Context
<!-- Why is this change needed? What problem does it solve? -->
This is outdated.

## How Has This Been Tested?
<!-- Have you tested this in a real application? Which scenarios were tested? -->
N/A

## Breaking Changes
<!-- Will users need to update their code or configurations? -->
N/A

## Types of changes
<!-- What types of changes does your code introduce? Put an `x` in all the boxes that apply: -->
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [x] Documentation update

## Checklist
<!-- Go over all the following points, and put an `x` in all the boxes that apply. -->
- [x] I have read the [MCP Documentation](https://modelcontextprotocol.io)
- [x] My code follows the repository's style guidelines
- [x] New and existing tests pass locally
- [x] I have added appropriate error handling
- [x] I have added or updated documentation as needed

## Additional context
<!-- Add any other context, implementation notes, or design decisions -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
