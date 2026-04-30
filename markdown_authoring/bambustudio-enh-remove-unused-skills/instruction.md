# ENH: remove unused skills

Source: [bambulab/BambuStudio#10392](https://github.com/bambulab/BambuStudio/pull/10392)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/jira-task/SKILL.md`

## What to add / change

jira: no-jira
Change-Id: Ie544b76aa14650b2fd6885d2c122be73192057d5

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
