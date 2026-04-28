# Some claude skills improvements

Source: [v112263/it-autonomos-spain#259](https://github.com/v112263/it-autonomos-spain/pull/259)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/tests-local-run-local-tests/SKILL.md`
- `.claude/skills/tests-local-test-and-update-internal-links/SKILL.md`
- `.claude/skills/tests-local-test-local-site-links/SKILL.md`
- `.claude/skills/tests-prod-run-prod-tests/SKILL.md`
- `.claude/skills/tests-prod-test-bitly-links/SKILL.md`
- `.claude/skills/tests-prod-test-prod-site-links/SKILL.md`
- `.claude/skills/tests-run-all-tests/SKILL.md`

## What to add / change

See the PR for the intended changes to the listed file(s).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
