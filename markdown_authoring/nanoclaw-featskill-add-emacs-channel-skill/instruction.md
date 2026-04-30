# feat(skill): add Emacs channel skill

Source: [qwibitai/nanoclaw#1375](https://github.com/qwibitai/nanoclaw/pull/1375)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/add-emacs/SKILL.md`

## What to add / change

## What

Adds the `add-emacs` feature skill. When invoked (`/add-emacs`), it merges the `skill/emacs` branch to add an Emacs channel via a lightweight local HTTP bridge, then walks through interactive setup.

Source code lives on the `skill/emacs` branch: `src/channels/emacs.ts`, `src/channels/emacs.test.ts`, `emacs/nanoclaw.el`, and the `src/channels/index.ts` import.

## Why

Emacs users spend most of their time in the editor. This gives them a first-class NanoClaw interface without switching to a messaging app — including inline org-mode integration.

## How tested

- 40 unit tests on the skill branch
- End-to-end tested with Doom Emacs

- [x] Feature skill

Co-Authored-By: Ken Bolton <ken@bscientific.com>
Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
