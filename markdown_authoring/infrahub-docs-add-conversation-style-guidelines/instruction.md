# docs: add conversation style guidelines to AGENTS.md

Source: [opsmill/infrahub#8443](https://github.com/opsmill/infrahub/pull/8443)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## <!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Documentation**
  * Added conversation-style requirements and a list of prohibited phrases in developer guidelines.
  * Updated technical stack details: frontend build tool bumped to v7.3, testing framework to v9.0, and linter to v0.15; other stack entries unchanged.
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

- Adds a "Conversation Style" section to the root AGENTS.md with explicit directives for AI agent communication tone
- Prohibits filler phrases, compliments, and social pleasantries (with specific examples)
- Requires direct responses, constructive criticism, and clarifying questions over guessing

## Test plan

- [ ] Verify AGENTS.md renders correctly on GitHub
- [ ] Confirm new section is picked up by Claude Code in a fresh session

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
