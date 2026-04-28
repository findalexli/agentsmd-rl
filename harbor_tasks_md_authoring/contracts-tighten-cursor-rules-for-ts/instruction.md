# tighten cursor rules for ts file edits

Source: [lifinance/contracts#1608](https://github.com/lifinance/contracts/pull/1608)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/099-finish.mdc`
- `.cursor/rules/200-typescript.mdc`

## What to add / change

# Which Jira task belongs to this PR?

# Why did I implement it this way?

# Checklist before requesting a review

- [x] I have performed a self-review of my code
- [x] This pull request is as small as possible and only tackles one problem
- [ ] I have added tests that cover the functionality / test the bug
- [ ] For new facets: I have checked all points from this list: https://www.notion.so/lifi/New-Facet-Contract-Checklist-157f0ff14ac78095a2b8f999d655622e
- [ ] I have updated any required documentation

# Checklist for reviewer (DO NOT DEPLOY and contracts BEFORE CHECKING THIS!!!)

- [ ] I have checked that any arbitrary calls to external contracts are validated and or restricted
- [ ] I have checked that any privileged calls (i.e. storage modifications) are validated and or restricted
- [ ] I have ensured that any new contracts have had AT A MINIMUM 1 preliminary audit conducted on <date> by <company/auditor>

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
