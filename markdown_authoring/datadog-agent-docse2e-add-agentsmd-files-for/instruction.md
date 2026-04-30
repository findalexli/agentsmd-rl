# docs(e2e): Add AGENTS.md files for E2E framework and fakeintake, and write-e2e skill

Source: [DataDog/datadog-agent#47585](https://github.com/DataDog/datadog-agent/pull/47585)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/write-e2e/SKILL.md`
- `AGENTS.md`
- `test/e2e-framework/AGENTS.md`
- `test/e2e-framework/CLAUDE.md`
- `test/fakeintake/AGENTS.md`
- `test/fakeintake/CLAUDE.md`

## What to add / change

## Summary

- **`test/e2e-framework/AGENTS.md`**: API reference for the E2E framework — environments, provisioners, agentparams, BaseSuite, custom environments, validation workflow
- **`test/fakeintake/AGENTS.md`**: API reference for fakeintake — supported endpoints, client usage, how to add new payload types
- **`.claude/skills/write-e2e/SKILL.md`**: Routing table + checklist for writing E2E tests (points agents to the right docs rather than duplicating knowledge)
- **Root `AGENTS.md`**: Added E2E testing section, file hierarchy for AI context, self-improvement expectations

## Test plan

- [ ] Verify docs are accurate by reading referenced source files
- [ ] Invoke `/write-e2e` skill and confirm it routes to the right docs
- [ ] Check that no guidance is duplicated across hierarchy levels

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
