# feat: add Spanish caveman mode (caveman-es)

Source: [JuliusBrussee/caveman#27](https://github.com/JuliusBrussee/caveman/pull/27)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/caveman-es/SKILL.md`

## What to add / change

## Summary

Adds `skills/caveman-es/SKILL.md` - a Spanish language variant of the caveman skill.

## How it works

Same structure as the English caveman skill with three intensity levels (lite, full, ultra). Spanish grammar rules replace English ones: drops articles (el/la/los), filler words (simplemente/básicamente), and pleasantries. Technical terms stay in English since that's how most Spanish-speaking devs use them.

## Examples

Normal: "El problema que estás experimentando probablemente se debe a..."
Caveman: "Bug en middleware auth. Verificación expiración token usa `<` no `<=`. Fix:"

Activated via `/caveman-es` or "modo cavernícola".

Fixes #8

This contribution was developed with AI assistance (Claude Code).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
