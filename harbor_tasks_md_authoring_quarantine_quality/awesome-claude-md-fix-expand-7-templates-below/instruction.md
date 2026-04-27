# fix: expand 7 templates below 50-line minimum to pass validation

Source: [sx4im/awesome-claude-md#4](https://github.com/sx4im/awesome-claude-md/pull/4)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `templates/conventional-changelog/CLAUDE.md`
- `templates/knip/CLAUDE.md`
- `templates/lint-staged/CLAUDE.md`
- `templates/oklch-colors/CLAUDE.md`
- `templates/renovate/CLAUDE.md`
- `templates/simple-git-hooks/CLAUDE.md`
- `templates/verdaccio/CLAUDE.md`

## What to add / change

conventional-changelog, knip, lint-staged, oklch-colors, renovate, simple-git-hooks, and verdaccio each added a File Naming section and expanded Testing guidance so all 400 templates now pass validate.py.

https://claude.ai/code/session_011G6PNY8JJsPhio7SZYD9kf

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
