# chore(x-engage): drop disclosure line from X replies

Source: [OpenRouterTeam/spawn#3335](https://github.com/OpenRouterTeam/spawn/pull/3335)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/setup-agent-team/x-engage-prompt.md`

## What to add / change

## Summary
- Removes the "(disclosure: i help build this)" instruction from the X engagement prompt (`x-engage-prompt.md`)
- X/Twitter replies now post as-is without any attribution footer
- Reddit growth prompt (`growth-prompt.md`) still keeps its disclosure requirement — only X was changed per request

## Test plan
- [ ] Next X engagement cycle drafts a reply without the disclosure line

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
