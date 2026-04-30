# docs(skills): add gh and gh-skill agent skills

Source: [cli/cli#13244](https://github.com/cli/cli/pull/13244)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/gh-skill/SKILL.md`
- `skills/gh/SKILL.md`

## What to add / change

## Description

Adds two `SKILL.md` files in the canonical `skills/` publishing location so this repo can be installed as a skill source via `gh skill install cli/cli <skill>`.

- **`skills/gh/SKILL.md`** - lean guide to the agentic pain points of using `gh` as a whole. 
- **`skills/gh-skill/SKILL.md`** - lean self-management guide so an agent can use `gh skill` to discover/preview/install/update/publish its own skills.

## Notes

I'm intentionally not inflating these skill files with exhaustive data that most models already know about. Let's focus on the pain points, keep the token consumption lean.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
