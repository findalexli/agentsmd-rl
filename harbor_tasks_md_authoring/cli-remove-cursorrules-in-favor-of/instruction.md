# Remove .cursorrules in favor of AGENTS.md

Source: [databricks/cli#3559](https://github.com/databricks/cli/pull/3559)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursorrules`

## What to add / change

Remove the .cursorrules symlink as [Cursor now supports AGENTS.md](https://docs.cursor.com/en/context/rules) directly for defining agent behavior.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
