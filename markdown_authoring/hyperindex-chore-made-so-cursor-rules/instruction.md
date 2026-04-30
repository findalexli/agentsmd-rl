# chore: made so cursor rules is downloaded on init

Source: [enviodev/hyperindex#778](https://github.com/enviodev/hyperindex/pull/778)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/subgraph-migration.mdc`
- `codegenerator/cli/templates/static/shared/.cursor/rules/subgraph-migration.mdc`

## What to add / change

Updated subgraph-migration.mdc file to latest version and made so downloaded on init.

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

- Documentation
  - Added a comprehensive, mandatory migration guide for subgraphs to Envio HyperIndex with step-by-step workflow.
  - Introduced a CRITICAL requirement to use the Effect API for all external calls, with guidance on batching, error handling, context usage, and caching.
  - Enforced exact filename/structure matching, prohibited TODOs in final steps, and added an expanded runtime testing checklist and a new environment-variable setup step.
  - Tightened validation, examples, and wording across migration instructions.
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
