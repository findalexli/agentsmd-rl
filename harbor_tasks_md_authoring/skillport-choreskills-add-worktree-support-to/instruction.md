# chore(skills): add worktree support to git-branch-cleanup skill

Source: [gotalab/skillport#72](https://github.com/gotalab/skillport/pull/72)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.skills/experimental/git-branch-cleanup/SKILL.md`

## What to add / change

## Description & Motivation
Add git worktree handling to the git-branch-cleanup skill. Branches with associated worktrees require special handling before deletion.

## Changes
- Add compatibility note for git version requirements
- Add worktree detection commands (git worktree list, branch prefix check)
- Add "Has Worktree" category to branch classification table
- Add worktree removal instructions before branch deletion
- Add bulk delete script with automatic worktree handling
- Add worktree commands to reference section
- Add worktree check to safety checklist

## How to Test
CI only

## Checklist
- [x] Lint passes
- [x] Tests pass
- [x] Docs updated (if behavior changed)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
