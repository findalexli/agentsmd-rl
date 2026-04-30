# Add context checkpoints, iteration prompt, and parallel autopilot

Source: [garagon/nanostack#64](https://github.com/garagon/nanostack/pull/64)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `compound/SKILL.md`
- `plan/SKILL.md`
- `qa/SKILL.md`
- `review/SKILL.md`
- `security/SKILL.md`
- `ship/SKILL.md`
- `think/SKILL.md`

## What to add / change

## Summary

Two issues found during live sprint testing:

**1. context_checkpoint missing from artifacts**
All 7 skills now include `context_checkpoint` (summary, key_files, decisions_made, open_questions) in their save-artifact instruction. Previously this was only documented in conductor/SKILL.md Phase Protocol but individual skills didn't include it, so artifacts saved during autopilot sprints had no checkpoints.

**2. No result preview after ship**
Ship skill now tells the user how to view the result based on project type (HTML file, web app, CLI tool). Uses text instructions only. Never auto-opens URLs or executes `open` commands (scanner-safe).

## Test plan

- [x] All 7 SKILL.md files include context_checkpoint in save-artifact instruction
- [x] Ship SKILL.md has "Show the result" section with HTML/web/CLI examples
- [x] No `open` commands or URL auto-launching in any SKILL.md
- [x] No absolute paths (all still use relative bin/ with Script Resolution)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
