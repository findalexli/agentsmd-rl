# docs: Potential fixes for 3 code quality findings

Source: [IJHack/QtPass#1182](https://github.com/IJHack/QtPass/pull/1182)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.opencode/skills/qtpass-github/SKILL.md`

## What to add / change

<!-- kody-pr-summary:start -->
Updated Git commands in `SKILL.md` to improve clarity and efficiency for common workflows:

*   Replaced `git fetch upstream` with `git pull upstream main --rebase` for updating a branch with `main`, streamlining the fetch and rebase process into a single command.
*   Added `git checkout <branch>` before fetch and rebase operations when resolving conflicts, ensuring the user is on the correct branch.
*   Removed a redundant `git fetch upstream` command before `git pull upstream main --rebase`, as `git pull` inherently includes a fetch operation.
<!-- kody-pr-summary:end -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
