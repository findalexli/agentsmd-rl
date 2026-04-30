# docs: Update AGENTS.md

Source: [modelcontextprotocol/kotlin-sdk#509](https://github.com/modelcontextprotocol/kotlin-sdk/pull/509)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

# docs: Update AGENTS.md

- Introduce CLAUDE.md symlink to AGENTS.md
- Enhance AGENTS.md with updated test setup, coding standards, and module-specific practices

## Motivation and Context

Motivation: Improve consistency, readability, and maintainability of code contributions across AI agents and developers.

## Breaking Changes
No

## Types of changes

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [x] Documentation update

## Checklist
- [x] I have read the [MCP Documentation](https://modelcontextprotocol.io)
- [x] My code follows the repository's style guidelines
- [x] New and existing tests pass locally
- [ ] I have added appropriate error handling
- [x] I have added or updated documentation as needed

## Verified

<img width="584" height="225" alt="image" src="https://github.com/user-attachments/assets/591202a3-56aa-4901-ad5d-9e2d4b9f0013" />

(I have other files locally, but AGENTS.md is known to Claude)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
