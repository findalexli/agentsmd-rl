# plugin: incorporate describegpt into agents, skills & commands

Source: [dathere/qsv#3626](https://github.com/dathere/qsv/pull/3626)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/agents/data-analyst.md`
- `.claude/skills/commands/data-describe.md`
- `.claude/skills/commands/data-profile.md`
- `.claude/skills/skills/csv-wrangling/SKILL.md`
- `.claude/skills/skills/data-quality/SKILL.md`

## What to add / change

Add qsv_describegpt references across the plugin so users get guided toward AI-powered Data Dictionary, Description & Tags generation:

- data-analyst agent: add tool, workflow step 8, analysis capabilities mention
- /data-profile command: add tool, step 10, report format & checklist items
- /data-describe command: new dedicated command for describegpt workflows
- csv-wrangling skill: add workflow step 8, tool matrix entry, pipeline pattern
- data-quality skill: add Documentation quality dimension

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
