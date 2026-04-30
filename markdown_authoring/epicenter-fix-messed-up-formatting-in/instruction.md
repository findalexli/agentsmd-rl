# fix: messed up formatting in AGENTS.md.

Source: [EpicenterHQ/epicenter#887](https://github.com/EpicenterHQ/epicenter/pull/887)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

- Nested ```` ``` ```` fixed by using ``` ```` ``` (four backticks) for outer code block.
- Fixes: https://github.com/epicenter-md/epicenter/issues/827
- Paves the way to organizing/splitting up AGENTS.md file. (GitHub outline/table of contents is now coherent)

## After fix:
<img width="1048" height="1102" alt="image" src="https://github.com/user-attachments/assets/221faf6c-5900-4983-bd85-f87c93d66db9" />

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
