# [codex] Add Codex OpenSpec skills

Source: [webspatial/webspatial-sdk#1135](https://github.com/webspatial/webspatial-sdk/pull/1135)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.codex/skills/openspec-apply-change/SKILL.md`
- `.codex/skills/openspec-archive-change/SKILL.md`
- `.codex/skills/openspec-explore/SKILL.md`
- `.codex/skills/openspec-propose/SKILL.md`

## What to add / change

## Summary

Add Codex-local OpenSpec skill definitions under `.codex/skills/` for common change workflows.

## Changes

- add `openspec-apply-change`
- add `openspec-archive-change`
- add `openspec-explore`
- add `openspec-propose`

## Scope

This PR only adds the `.codex` OpenSpec skill files.
It does not include `AGENTS.md` edits or the `openspec/changes/codex-review-integration/` worktree changes.

## Validation

- verified the branch diff against `main` contains only the 4 `.codex` files
- verified the staged commit scope before commit
- pre-commit checks passed during `git commit`

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
