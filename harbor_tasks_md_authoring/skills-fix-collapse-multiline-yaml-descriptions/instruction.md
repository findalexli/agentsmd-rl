# fix: collapse multiline YAML descriptions in SKILL.md files

Source: [posit-dev/skills#50](https://github.com/posit-dev/skills/pull/50)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `brand-yml/SKILL.md`
- `posit-dev/critical-code-reviewer/SKILL.md`
- `posit-dev/describe-design/SKILL.md`
- `quarto/quarto-alt-text/SKILL.md`
- `quarto/quarto-authoring/SKILL.md`
- `r-lib/lifecycle/SKILL.md`
- `r-lib/mirai/SKILL.md`
- `r-lib/r-cli-app/SKILL.md`
- `r-lib/r-package-development/SKILL.md`
- `r-lib/testing-r-packages/SKILL.md`

## What to add / change

Fixes #49

## Summary
Collapses multiline YAML `description` fields in 9 SKILL.md files into single-line strings. Also adds `model` and `temperature` metadata to the `r-package-development` skill. Many tools don't correctly handle multiline YAML block scalars (`>` or `|`), so keeping descriptions on one line improves compatibility.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
