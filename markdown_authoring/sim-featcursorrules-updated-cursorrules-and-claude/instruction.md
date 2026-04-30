# feat(cursorrules): updated cursorrules and claude md file

Source: [simstudioai/sim#2640](https://github.com/simstudioai/sim/pull/2640)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/emcn-components.mdc`
- `.cursor/rules/global.mdc`
- `.cursor/rules/sim-architecture.mdc`
- `.cursor/rules/sim-components.mdc`
- `.cursor/rules/sim-hooks.mdc`
- `.cursor/rules/sim-imports.mdc`
- `.cursor/rules/sim-integrations.mdc`
- `.cursor/rules/sim-queries.mdc`
- `.cursor/rules/sim-stores.mdc`
- `.cursor/rules/sim-styling.mdc`
- `.cursor/rules/sim-testing.mdc`
- `.cursor/rules/sim-typescript.mdc`
- `CLAUDE.md`

## What to add / change

## Summary
- updated cursorrules and claude md file

## Type of Change
- [x] Documentation

## Testing
N/A

## Checklist
- [x] Code follows project style guidelines
- [x] Self-reviewed my changes
- [ ] Tests added/updated and passing
- [x] No new warnings introduced
- [x] I confirm that I have read and agree to the terms outlined in the [Contributor License Agreement (CLA)](./CONTRIBUTING.md#contributor-license-agreement-cla)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
