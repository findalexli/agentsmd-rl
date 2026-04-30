# chore: refresh CLAUDE.md

Source: [modelcontextprotocol/typescript-sdk#1217](https://github.com/modelcontextprotocol/typescript-sdk/pull/1217)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Updates CLAUDE.md according to the latest code, as it hasn't been updated in a few eons.

Updated via /init on Claude Opus 4.5 with some follow-up revisions to cover the message flow and client details in more detail, as those are frequent points of errors.

## Motivation and Context
Existing CLAUDE.md was extremely outdated. Hopefully this avoids some common mistakes like trying to use Jest functions and misinterpreting how the Protocol class behaves.

## How Has This Been Tested?
N/A

## Breaking Changes
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
