# Add agents.md for running the app

Source: [nekomangaorg/Neko#2328](https://github.com/nekomangaorg/Neko/pull/2328)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `agents.md`

## What to add / change

This change adds a new `agents.md` file to the root of the repository. This file contains detailed instructions on how to get the application running, which will be helpful for new developers and for automated agents like myself.

---
*PR created automatically by Jules for task [647087725625216150](https://jules.google.com/task/647087725625216150)*

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
