# fix: use hyphenated name in SKILL.md

Source: [BehiSecc/VibeSec-Skill#5](https://github.com/BehiSecc/VibeSec-Skill/pull/5)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`

## What to add / change

Changed name: vibe security skill → name: vibe-security-skill 
Spaces in the name field break direct skill imports in Claude

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
