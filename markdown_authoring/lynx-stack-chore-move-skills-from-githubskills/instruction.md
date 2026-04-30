# chore: move skills from .github/skills to .agents/skills

Source: [lynx-family/lynx-stack#2522](https://github.com/lynx-family/lynx-stack/pull/2522)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/pr-ci-watch-subagent/SKILL.md`

## What to add / change

Agent skills belong under `.agents/skills`, not `.github/skills`.

This moves `pr-ci-watch-subagent` to the correct location.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
