# Add full-cli-test agent skill with Slack integration tests

Source: [ComposioHQ/composio#3081](https://github.com/ComposioHQ/composio/pull/3081)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/cli-test-with-bundling/SKILL.md`
- `.claude/skills/full-cli-test/SKILL.md`

## What to add / change

## Summary

- Adds new `/full-cli-test` agent skill that orchestrates a 3-phase CLI validation pipeline: poll CI for type/lint → local binary test → CI-bundled binary test
- Includes a Slack integration test (`#buzz-skill-based-cli-testing`) that validates `execute()`, `experimental_subAgent()`, `z` (Zod), and `result.prompt()` in both local and bundled builds
- Updates `/cli-test-with-bundling` to always use `-beta.<timestamp>` versioning, preventing accidental production releases from test runs

## Test plan

- [ ] Verify `/full-cli-test` skill appears in skill list
- [ ] Run `/cli-test-with-bundling` and confirm the workflow dispatch uses a beta version
- [ ] Confirm the Slack test script runs against `#buzz-skill-based-cli-testing`

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
