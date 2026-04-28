# Improved agents.md

Source: [andreasgriffin/bitcoin-safe#606](https://github.com/andreasgriffin/bitcoin-safe/pull/606)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Required

- `pre-commit install` before any commit. If pre-commit wasn't run for all commits, you can squash all commits   `git reset --soft $(git merge-base main HEAD) && git commit -m "squash"` and ensure the squashed commit is properly formatted
- All commits must be signed. If some are not, you can squash all commits   `git reset --soft $(git merge-base main HEAD) && git commit -m "squash"` and ensure the squashed commit is signed
- [ ] UI/Design/Menu changes **were** tested on _macOS_, because _macOS_ creates endless problems.  Optionally attach a screenshot.
 
## Optional

- [ ] Update all translations
- [ ] Appropriate pytests were added
- [ ] Documentation is updated
- [ ] If this PR affects builds or install artifacts, set the `Build-Relevant` label to trigger build workflows

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
