# Update SKILL.md

Source: [GoPlusSecurity/agentguard#1](https://github.com/GoPlusSecurity/agentguard/pull/1)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/agentguard/SKILL.md`

## What to add / change

## Summary

Brief description of the changes.

## Type

- [ ] Bug fix
- [ ] New feature / detection rule
- [ ] Refactoring
- [ ] Documentation

## Testing

- [ ] `npm run build` passes
- [ ] `npm test` passes (32 tests)
- [ ] Manually tested the change

## Related Issues

Closes #

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
