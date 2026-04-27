# Recommend generate-report for crypto reports

Source: [besoeasy/open-skills#4](https://github.com/besoeasy/open-skills/pull/4)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/city-distance/SKILL.md`
- `skills/get-crypto-price/SKILL.md`

## What to add / change

Update get-crypto-price skill to instruct agents to use skills/generate-report for formatted outputs (markdown/PDF) so reports are consistent. This helps other agents detect and reuse the reporting skill.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
