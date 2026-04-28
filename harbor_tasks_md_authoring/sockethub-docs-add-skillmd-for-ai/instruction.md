# docs: add SKILL.md for AI agent discoverability

Source: [sockethub/sockethub#1001](https://github.com/sockethub/sockethub/pull/1001)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`

## What to add / change

## Summary

- Adds SKILL.md following the [Anthropic Agent Skills specification](https://github.com/anthropics/skills)
- Enables AI agents to discover and use sockethub for building messaging applications
- Documents IRC, XMPP, and RSS/Atom platform usage with concrete examples

## What is SKILL.md?

SKILL.md files make npm packages discoverable by AI agents. They provide structured documentation that helps agents understand:
- **When** to use the package (trigger conditions)
- **How** to use it (quick start, examples)
- **What** it does (capabilities, API reference)

## Test plan

- [ ] Verify SKILL.md renders correctly on GitHub
- [ ] Confirm description is under 1024 characters
- [ ] Validate examples are accurate for current API

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
