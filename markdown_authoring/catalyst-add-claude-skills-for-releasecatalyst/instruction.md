# Add Claude skills for release-catalyst and sync-makeswift

Source: [bigcommerce/catalyst#2922](https://github.com/bigcommerce/catalyst/pull/2922)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/release-catalyst/SKILL.md`
- `.claude/skills/sync-makeswift/SKILL.md`

## What to add / change

## Summary

- Adds a `release-catalyst` skill that orchestrates the full two-stage release process: merging the Version Packages PR on canary, syncing integrations/makeswift, and pushing @latest tags.
- Adds a `sync-makeswift` skill that automates syncing the `integrations/makeswift` branch with `canary`, including conflict resolution rules and the rebase-based merge workflow.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
