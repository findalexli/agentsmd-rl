# fix(pr-research): add push access verification

Source: [boshu2/agentops#9](https://github.com/boshu2/agentops/pull/9)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/pr-kit/skills/pr-research/SKILL.md`

## What to add / change

## Summary

- Adds explicit push access verification guidance to `/pr-research` skill
- Requires `gh repo view --json viewerPermission` check before assuming workflow
- Prevents false "you have push access" messages

## Fixes

Closes #8 - skill incorrectly assumed user had push access to external repo based on workspace context

## Changes

Added new "Push Access Verification" section with:
- Command to check actual permissions
- Permission level table (ADMIN/WRITE = push, READ/NONE = fork)
- Anti-pattern entry for assuming push access
- Explicit guidance to never assume access without verification

## Test plan

- [ ] Run `/pr-research` on a repo you don't have push access to
- [ ] Verify it recommends fork-based workflow

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
