# docs: add test conventions to AGENTS.md

Source: [StarCitizenTools/mediawiki-skins-Citizen#1320](https://github.com/StarCitizenTools/mediawiki-skins-Citizen/pull/1320)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary
- Add a general **Tests** section with Arrange-Act-Assert convention (applies to both PHPUnit and Vitest)
- Note JS tests use Vitest under the JavaScript section

## Test plan
- [x] AGENTS.md renders correctly

🤖 Generated with [Claude Code](https://claude.com/claude-code)

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Documentation**
  * Updated testing guidance documentation with recommended testing patterns and framework clarifications.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
