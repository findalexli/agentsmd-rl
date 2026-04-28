# Fix/skills cli alignment

Source: [DingTalk-Real-AI/dingtalk-workspace-cli#158](https://github.com/DingTalk-Real-AI/dingtalk-workspace-cli/pull/158)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/references/products/report.md`

## What to add / change

## Summary

- What changed?
- Why is this change needed?

## Verification

- [ ] `make build`
- [ ] `make lint`
- [ ] `make test`
- [ ] `make policy`
- [ ] `./scripts/policy/check-generated-drift.sh`
- [ ] `./scripts/policy/check-command-surface.sh --strict` (if command surface changed)

## Notes

- Any risks, follow-up work, or intentional scope cuts

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
