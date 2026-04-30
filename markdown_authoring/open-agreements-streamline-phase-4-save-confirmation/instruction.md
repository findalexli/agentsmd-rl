# Streamline Phase 4: save confirmation PDF as filing record

Source: [open-agreements/open-agreements#66](https://github.com/open-agreements/open-agreements/pull/66)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/delaware-franchise-tax/SKILL.md`

## What to add / change

## Summary
- Replace separate filing record step with guidance to save the portal's confirmation PDF to a durable location
- The PDF already contains all filing details (entity, file number, tax year, method, amount, service request number)
- Suggest default paths (`~/Documents/Tax/Delaware/<EntityName>/`) and cloud storage alternatives

## Test plan
- [ ] Verify SKILL.md renders correctly
- [ ] Confirm Phase 4 instructions are clear and actionable

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
