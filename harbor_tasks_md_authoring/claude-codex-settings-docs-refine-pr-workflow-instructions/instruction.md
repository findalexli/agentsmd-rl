# docs: refine PR workflow instructions for clarity

Source: [fcakyon/claude-codex-settings#13](https://github.com/fcakyon/claude-codex-settings/pull/13)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/agents/pr-manager.md`
- `CLAUDE.md`

## What to add / change

Improve PR workflow documentation clarity and accuracy.

- Clarify staged changes are optional when creating PRs ([.claude/agents/pr-manager.md:14-16](.claude/agents/pr-manager.md#L14-L16), [CLAUDE.md:78](.CLAUDE.md#L78))
- Focus workflow on analyzing complete branch diff to target ([.claude/agents/pr-manager.md:27-29](.claude/agents/pr-manager.md#L27-L29), [CLAUDE.md:81](.CLAUDE.md#L81))
- Add "enhanced" to forbidden AI words list ([CLAUDE.md:19](CLAUDE.md#L19))
- Improve reviewer selection guidance to reference assignee's PRs ([.claude/agents/pr-manager.md:44](.claude/agents/pr-manager.md#L44))

These changes align the documentation with the actual workflow where PR creation focuses on the full branch diff rather than requiring staged changes upfront.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
