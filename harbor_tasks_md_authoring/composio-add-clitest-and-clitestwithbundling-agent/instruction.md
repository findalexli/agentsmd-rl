# Add cli-test and cli-test-with-bundling agent skills

Source: [ComposioHQ/composio#3080](https://github.com/ComposioHQ/composio/pull/3080)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/cli-test-with-bundling/SKILL.md`
- `.agents/skills/cli-test/SKILL.md`
- `.claude/skills/cli-test-with-bundling/SKILL.md`
- `.claude/skills/cli-test/SKILL.md`

## What to add / change

## Summary

- Adds `cli-test` skill: build the CLI binary locally and test it directly
- Adds `cli-test-with-bundling` skill: trigger CI binary build via workflow dispatch, monitor, download artifact, test `run`/`subAgent`, and post results as a PR comment
- Both symlinked to `.agents/skills/` for Codex compatibility

## Test plan

- [ ] Verify `/cli-test` skill loads and instructions are accurate
- [ ] Verify `/cli-test-with-bundling` skill loads and instructions are accurate
- [ ] Verify symlinks resolve correctly in `.agents/skills/`

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
