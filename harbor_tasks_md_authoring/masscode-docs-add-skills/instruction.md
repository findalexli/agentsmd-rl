# docs: add skills

Source: [massCodeIO/massCode#754](https://github.com/massCodeIO/massCode/pull/754)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/api-and-typing/SKILL.md`
- `.agents/skills/architecture-standards/SKILL.md`
- `.agents/skills/development-workflow/SKILL.md`
- `.agents/skills/electron-api-and-ipc/SKILL.md`
- `.agents/skills/github-workflow/SKILL.md`
- `.agents/skills/i18n/SKILL.md`
- `.agents/skills/spaces-architecture/SKILL.md`
- `.agents/skills/ui-foundations/SKILL.md`
- `.agents/skills/ui-primitives/SKILL.md`
- `.agents/skills/vue-renderer-standards/SKILL.md`
- `AGENTS.md`

## What to add / change

See the PR for the intended changes to the listed file(s).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
