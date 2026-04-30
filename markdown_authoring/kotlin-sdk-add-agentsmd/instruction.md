# Add AGENTS.md

Source: [modelcontextprotocol/kotlin-sdk#349](https://github.com/modelcontextprotocol/kotlin-sdk/pull/349)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Introduce `AGENTS.md` documenting repository layout, build/test commands, API compatibility checks, code conventions, logging/error handling guidance, and the PR/review checklist for the Kotlin MCP SDK.

## Motivation and Context
Provide a single, authoritative reference for code agents.

## How Has This Been Tested?
-

## Breaking Changes
None

## Types of changes
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [x] Documentation update

## Checklist
- [x] I have read the [MCP Documentation](https://modelcontextprotocol.io)
- [x] My code follows the repository's style guidelines
- [ ] New and existing tests pass locally
- [ ] I have added appropriate error handling
- [x] I have added or updated documentation as needed

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
