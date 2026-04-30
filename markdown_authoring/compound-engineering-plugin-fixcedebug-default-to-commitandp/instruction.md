# fix(ce-debug): default to commit-and-PR and tighten learning offer

Source: [EveryInc/compound-engineering-plugin#693](https://github.com/EveryInc/compound-engineering-plugin/pull/693)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/ce-debug/SKILL.md`

## What to add / change

## Summary

ce-debug now defaults to commit-and-PR when it owns the working branch, and only offers `/ce-compound` when there is an articulable lesson worth capturing. Previously it closed every run with a 4-option prompt and prompted for learning capture on every bug. Both were over-eager: the common choice was nearly always "commit and open a PR", and the "bug was in production" trigger gating learning capture fired on essentially every issue, making the lean-in/neutral distinction meaningless.

## Skill-owned branches default to commit-and-PR

When ce-debug created the working branch in Phase 3, Phase 4 now proceeds straight to commit-and-PR with a brief, non-blocking preview. No menu, no confirmation prompt. Before doing so it checks the user's prompt, loaded memories, and `AGENTS.md`/`CLAUDE.md` for conflicting preferences (e.g., "always review before pushing", "open PRs as drafts") and honors them.

Pre-existing branches still get a smaller menu (commit & PR / commit only / stop) since ce-debug does not know what else might be staged on them.

The "Post findings to the issue first" option is gone. Tracker auto-close syntax in the PR description (`Fixes #N`, `Closes ABC-123`, Jira Smart Commits) puts the diagnosis on the issue and closes it on merge, so a separate "post findings" step just duplicates what the PR will already do.

## Learning capture is now gated on articulability

`/ce-compound` is no longer offered after every bug. The new gate has three paths:

| Path 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
