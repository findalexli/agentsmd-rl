# fix(agile-product-owner): add boundaries and triggers

Source: [alirezarezvani/claude-skills#521](https://github.com/alirezarezvani/claude-skills/pull/521)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `product-team/agile-product-owner/SKILL.md`

## What to add / change

## Summary

Fixes #504.

Adds a not_for boundary, three trigger keywords, and a short differentiation section so the skill is selected and scoped correctly.

## Checklist

- [x] **Target branch is `dev`** (not `main` — PRs to main will be auto-closed)
- [x] Skill has `SKILL.md` with valid YAML frontmatter (`name`, `description`, `license`)
- [x] Scripts (if any) run with `--help` without errors
- [x] No hardcoded API keys, tokens, or secrets
- [x] No vendor-locked dependencies without open-source fallback
- [x] Follows existing directory structure (`domain/skill-name/SKILL.md`)

## Type of Change

- [ ] New skill
- [x] Improvement to existing skill
- [ ] Bug fix
- [ ] Documentation
- [ ] Infrastructure / CI

## Testing

Not run (content-only update).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
