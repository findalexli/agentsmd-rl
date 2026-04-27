# fix: clarify next-task skill triggers

Source: [agent-sh/agentsys#218](https://github.com/agent-sh/agentsys/pull/218)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `adapters/opencode/skills/discover-tasks/SKILL.md`
- `adapters/opencode/skills/orchestrate-review/SKILL.md`
- `adapters/opencode/skills/validate-delivery/SKILL.md`
- `plugins/next-task/skills/discover-tasks/SKILL.md`
- `plugins/next-task/skills/orchestrate-review/SKILL.md`
- `plugins/next-task/skills/validate-delivery/SKILL.md`

## What to add / change

Amp-Thread-ID: https://ampcode.com/threads/T-019c58d6-7447-76d1-8e5b-c1c0e03cac36
Co-authored-by: Amp <amp@ampcode.com>

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
