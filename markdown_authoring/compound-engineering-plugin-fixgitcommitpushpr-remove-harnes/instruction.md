# fix(git-commit-push-pr): remove harness slug from badge table

Source: [EveryInc/compound-engineering-plugin#539](https://github.com/EveryInc/compound-engineering-plugin/pull/539)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md`

## What to add / change

The harness slug in the badge was redundant — the logo and color already identify the harness. Removes the `HARNESS_SLUG` column from the lookup table and simplifies the badge template to just show the model name.

---

[![Compound Engineering](https://img.shields.io/badge/Built_with-Compound_Engineering-6366f1)](https://github.com/EveryInc/compound-engineering-plugin)
![Claude Code](https://img.shields.io/badge/Opus_4.6_(1M)-D97757?logo=claude&logoColor=white)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
