# docs: improve command-implementation skill discoverability

Source: [ruby-git/ruby-git#1223](https://github.com/ruby-git/ruby-git/pull/1223)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/skills/command-implementation/SKILL.md`

## What to add / change

Adds "class" to the "updating an existing command" trigger phrase in the \`command-implementation\` skill's frontmatter description, so the skill is reliably selected when users say "update command class".

**Before:**
> Use when creating a new command from scratch, **updating an existing command**, or reviewing a command class for correctness.

**After:**
> Use when creating a new command class from scratch, **updating an existing command class**, or reviewing a command class for correctness.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
