# [NA] [SDK] Opik Optimizer Cursor Rules and AGENT.md

Source: [comet-ml/opik#3895](https://github.com/comet-ml/opik/pull/3895)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `sdks/opik_optimizer/.cursor/rules/architecture.mdc`
- `sdks/opik_optimizer/.cursor/rules/code-structure.mdc`
- `sdks/opik_optimizer/.cursor/rules/dependencies.mdc`
- `sdks/opik_optimizer/.cursor/rules/documentation-style.mdc`
- `sdks/opik_optimizer/.cursor/rules/error-handling.mdc`
- `sdks/opik_optimizer/.cursor/rules/logging.mdc`
- `sdks/opik_optimizer/.cursor/rules/test-best-practices.mdc`
- `sdks/opik_optimizer/.cursor/rules/test-organization.mdc`

## What to add / change

## Details
Adding some healthy defaults to make AI agent and IDE coders more compatible with design choices in Opik Optimizer.

## Change checklist
- [x] User facing
- [x] Documentation update

## Issues

- Resolves #
- OPIK-

## Testing
n.a

## Documentation
n.a

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
