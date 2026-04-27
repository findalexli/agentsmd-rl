# docs(skills): improve gh-merge skill with CI safety and worktree support

Source: [AgentsMesh/AgentsMesh#91](https://github.com/AgentsMesh/AgentsMesh/pull/91)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/gh-merge/SKILL.md`

## What to add / change

## Summary

- Require CI checks to pass before merge (retry on "no checks reported" instead of assuming no CI)
- Detect correct GitHub remote name from `git remote -v` (not hardcoded to `origin`)
- Handle git worktree environment (stash before rebase, worktree-safe cleanup)
- Add explicit merge preconditions (at least 1 check reported, all pass, no conflicts)
- Prefer `git add <files>` over `git add .` to avoid accidental commits

## Context

Based on a real failure where PR #88 was merged before CI completed — `gh pr checks` returned "no checks reported" (CI hadn't triggered yet) and was misinterpreted as "no CI configured".

## Test plan

- [x] Documentation-only change, no code affected

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
