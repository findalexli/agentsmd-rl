# Docs: Add AGENTS.md file with comprehensive agent documentation

Source: [Azure/co-op-translator#247](https://github.com/Azure/co-op-translator/pull/247)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Purpose
Provide agent-focused documentation to help AI coding agents work effectively with this repository.

## Description
- Added `AGENTS.md` at the repository root.
- Included clear, actionable sections: Project Overview, Architecture overview, Setup Commands, Development Workflow, Testing Instructions, Code Style Guidelines, Build and Deployment, Security Considerations, Pull Request Guidelines, Debugging and Troubleshooting, Notes for Agents.
- Added a detailed “Required Environment Variables” section covering Azure OpenAI, OpenAI, and Azure AI Service (images), with a sample `.env`.
- Cross-referenced `getting_started/` docs (Azure setup and GitHub Actions guides).

## Related Issue
Fixes #246

## Does this introduce a breaking change?
- [ ] Yes
- [x] No

## Type of change
- [ ] Bugfix
- [ ] Feature
- [ ] Code style update (e.g., formatting, local variables)
- [ ] Refactoring (no functional or API changes)
- [x] Documentation content changes
- [ ] Other... Please describe:

## Checklist
- [ ] I have thoroughly tested my changes
- [ ] All existing tests pass
- [ ] I have added new tests (if applicable)
- [x] I have followed the Co-op Translators coding conventions
- [x] I have documented my changes (if applicable)

## Additional context
- Only `AGENTS.md` was added; no other files were modified.
- Guidance consolidates existing commands and environment configuration used by the project.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
