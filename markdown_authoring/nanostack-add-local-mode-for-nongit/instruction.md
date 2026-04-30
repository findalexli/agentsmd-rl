# Add local mode for non-git users

Source: [garagon/nanostack#85](https://github.com/garagon/nanostack/pull/85)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plan/SKILL.md`
- `review/SKILL.md`
- `ship/SKILL.md`
- `think/SKILL.md`

## What to add / change

## Summary

- Auto-detect git context and adapt the entire sprint for users working in local folders without git
- `bin/lib/git-context.sh` detects three modes: `full` (git + remote), `local-git` (git, no remote), `local` (no git)
- Skills adapt language for non-technical users: same rigor, simpler words
- Zero changes to the existing git workflow. Detection is runtime, not config.

## Why

The fastest growing segment using AI coding agents are non-developers: founders, operators, professionals building things with Cursor or Claude Code in local folders. They've never opened a terminal. The sprint flow (think, plan, build, review, ship) works for them, but review assumes git diff and ship assumes PR creation.

**Example:** A user building a landing page in `~/Desktop/my-project/`. After the build:
- Before: `/ship` says "Create a PR" → confusion. What's a PR?
- After: `/ship` says "Listo. Se abrió en tu navegador."

## What changes per skill

| Skill | Mode full (git + remote) | Mode local (no git) |
|-------|-------------------------|---------------------|
| /think | Unchanged | Same questions, plain language. Internal labels (Phase 1, Startup mode) hidden. |
| /nano | Unchanged | "Step by step" vs "implementation plan". No slash commands in next steps. |
| /review | Unchanged | Files from plan instead of git diff. "Encontré 5 cosas, 2 ya las arreglé" vs "5 findings (2 auto-fixed, 1 ask, 2 nits)". |
| /ship | Unchanged | Opens HTML directly. "Se abrió en tu navegador" vs "Cr

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
