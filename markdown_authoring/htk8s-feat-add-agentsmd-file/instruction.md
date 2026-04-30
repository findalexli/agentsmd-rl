# feat: Add AGENTS.md file

Source: [fabito/htk8s#55](https://github.com/fabito/htk8s/pull/55)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

This commit adds an AGENTS.md file to provide guidance to AI developers on how to work with this repository. The file includes instructions on the project structure, how to make changes, and how to regenerate the install manifests.

---
*PR created automatically by Jules for task [14614598788891687281](https://jules.google.com/task/14614598788891687281) started by @fabito*

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
