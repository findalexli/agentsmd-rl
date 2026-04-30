# Add router mode check section to SKILL.md

Source: [glitternetwork/pinme#34](https://github.com/glitternetwork/pinme/pull/34)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/pinme/SKILL.md`

## What to add / change

Document hash mode routing requirement for IPFS deployment to prevent 404 errors on sub-routes, with examples for React and Vue.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
