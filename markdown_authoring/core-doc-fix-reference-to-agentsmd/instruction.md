# doc: fix reference to AGENTS.md

Source: [api-platform/core#7743](https://github.com/api-platform/core/pull/7743)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

| Q             | A
| ------------- | ---
| Branch?       | main
| Tickets       | .
| License       | MIT
| Doc PR        | .

`tests/GEMINI.md` does not exist. The actual file is `AGENTS.md`: https://github.com/soyuka/core/blob/5c5d38f12fe0dfe0f1904f7af8706088fa711d1c/tests/AGENTS.md

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
