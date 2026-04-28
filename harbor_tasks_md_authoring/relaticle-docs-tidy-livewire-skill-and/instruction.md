# docs: tidy livewire skill and CLAUDE.md

Source: [relaticle/relaticle#240](https://github.com/relaticle/relaticle/pull/240)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/skills/livewire-development/SKILL.md`
- `CLAUDE.md`

## What to add / change

- Drop verbose v4 SFC path callouts and emoji notes from the livewire skill so it matches the project's actual conventions.
- Reorganize CLAUDE.md so the deployment note lives under the Laravel section instead of as a separate ruleset, and trim the Filament common-mistakes list.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
