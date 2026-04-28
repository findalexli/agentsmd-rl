# chore: add agents.md

Source: [Shelf-nu/shelf.nu#2044](https://github.com/Shelf-nu/shelf.nu/pull/2044)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary
- add a Documentation & Research section that directs contributors to review the docs/ folder before major work
- remind developers to incorporate relevant checklists from the docs into their implementation plans and PR notes

## Testing
- npm run db:generate-type
- npm run lint:fix
- npm run format
- npm run typecheck

------
https://chatgpt.com/codex/tasks/task_b_68cabf4b40a8832088436c4251d21ee1

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
