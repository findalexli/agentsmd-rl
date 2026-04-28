# docs: Update docs SKILL.md to match its own advice

Source: [mckinsey/agents-at-scale-ark#647](https://github.com/mckinsey/agents-at-scale-ark/pull/647)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/documentation/SKILL.md`

## What to add / change

Match the guidelines within the skill to the skill itself :)

## Checklist

- [x] Follow the [contributor guide](./CONTRIBUTING.md)
- [ ] End-to-end tests pass
- [ ] Unit tests for essential parts of your code, e.g. APIs exposed via SDKs or endpoints
- [x] Update `./docs`
- [ ] Recognize contributors with "@all-contributors please add <person> for <code, bug, docs, etc>"
- [ ] Linked issues #eg101

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
