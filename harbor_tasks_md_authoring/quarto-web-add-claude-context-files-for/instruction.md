# Add Claude context files for docs authoring

Source: [quarto-dev/quarto-web#1985](https://github.com/quarto-dev/quarto-web/pull/1985)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/rules/docs-authoring.md`
- `_extensions/prerelease/CLAUDE.md`

## What to add / change

Path-scoped Claude Code context files to help with docs workflows:

- `.claude/rules/docs-authoring.md` — prerelease shortcode usage guidance, scoped to `docs/**/*.qmd`
- `_extensions/prerelease/CLAUDE.md` — pointer to source and design PR for the extension

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
