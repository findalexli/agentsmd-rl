# docs: add AGENTS.md

Source: [UI5/webcomponents#13041](https://github.com/UI5/webcomponents/pull/13041)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`
- `packages/base/AGENTS.md`

## What to add / change

- **/AGENTS.md** for project structure and overview
- **/packages/base/AGENTS.md** for component development

- **/CLAUDE.md**  → Pointer file for Claude Code (@AGENTS.md)
- **/packages/base/CLAUDE.md**  → Pointer file for Claude Code (@AGENTS.md)

<img width="557" height="318" alt="Screenshot 2026-02-06 at 13 11 37" src="https://github.com/user-attachments/assets/376ec26c-620e-4f81-81f2-6aa997555e84" />

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
