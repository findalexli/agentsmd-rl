# Fix accessibility skill

Source: [microsoft/vscode#293548](https://github.com/microsoft/vscode/pull/293548)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/skills/accessibility/SKILL.md`

## What to add / change

It did not have the right folder structure.

## Old
<img width="822" height="535" alt="image" src="https://github.com/user-attachments/assets/d60eeee8-bd2f-4c42-93b0-f264646b83d9" />


## New
<img width="826" height="575" alt="image" src="https://github.com/user-attachments/assets/146dca92-5fb8-4cb8-a71a-daf6c12332e5" />

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
