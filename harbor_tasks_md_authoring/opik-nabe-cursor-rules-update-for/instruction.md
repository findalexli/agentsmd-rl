# [NA][BE] Cursor rules update for BE java code

Source: [comet-ml/opik#4155](https://github.com/comet-ml/opik/pull/4155)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `apps/opik-backend/.cursor/rules/code_style.mdc`

## What to add / change

## Details
Small cursor rules file update based on feedback from prior code reviews.

## Change checklist
- [ ] User facing
- [ ] Documentation update

## Issues

- Resolves #
- OPIK-0000

## Testing
n.a

## Documentation
n.a

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
