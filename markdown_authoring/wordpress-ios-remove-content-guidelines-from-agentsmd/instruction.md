# Remove Content Guidelines from AGENTS.md

Source: [wordpress-mobile/WordPress-iOS#25288](https://github.com/wordpress-mobile/WordPress-iOS/pull/25288)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

This is a left-over from https://github.com/wordpress-mobile/WordPress-iOS/commit/0d6051122976e073effbea3d16ce3b2b31382286 and release notes generation.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
