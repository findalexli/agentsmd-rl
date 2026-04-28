# docs: clarify squash merge preference and force push guidance

Source: [IJHack/QtPass#1176](https://github.com/IJHack/QtPass/pull/1176)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.opencode/skills/qtpass-github/SKILL.md`

## What to add / change

<!-- kody-pr-summary:start -->
This pull request updates the `.opencode/skills/qtpass-github/SKILL.md` documentation to provide clearer guidance on merging Pull Requests and using Git.

Key changes include:
- Explicitly stating a preference for squash merging for long PR threads to maintain a clean main branch history.
- Adding a detailed explanation of when to use squash merge versus a regular merge, including specific use cases for each strategy.
- Introducing a table summarizing different merge strategies (Squash, Merge, Rebase) and their recommended use cases.
- Providing updated GitHub CLI commands for both squash and regular merges.
- Adding clear guidance on avoiding force pushes to shared branches, especially `main`.
<!-- kody-pr-summary:end -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
