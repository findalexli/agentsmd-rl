# chore(cursor): convert rules to skills

Source: [Opentrons/opentrons#20886](https://github.com/Opentrons/opentrons/pull/20886)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/ai-server.mdc`
- `.cursor/skills/ai-server/SKILL.md`
- `.cursor/skills/analyses-snapshot-testing/SKILL.md`
- `.cursor/skills/components-testing/SKILL.md`
- `.cursor/skills/css-modules/SKILL.md`
- `.cursor/skills/e2e-testing/SKILL.md`
- `.cursor/skills/locize-sync/SKILL.md`
- `.cursor/skills/opentrons-typescript/SKILL.md`
- `.cursor/skills/protocol-designer/SKILL.md`
- `.cursor/skills/react-component-creation/SKILL.md`
- `.cursor/skills/robot-python-projects/SKILL.md`
- `.cursor/skills/static-deploy/SKILL.md`

## What to add / change

Read the documentation and realized this was as easy as telling the agent to `/migrate-to-skills`
Thanks @koji for telling me about this.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
