# chore: added subgraph migration mdc file to cursor rules

Source: [enviodev/hyperindex#725](https://github.com/enviodev/hyperindex/pull/725)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/subgraph-migration.mdc`

## What to add / change

chore: added subgraph migration mdc file to cursor rules

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

- Documentation
  - Added a comprehensive migration guide for converting TheGraph subgraphs to Envio HyperIndex.
  - Provides a step-by-step migration lifecycle, multichain indexing best practices, and patterns for entity and dynamic contract registration.
  - Covers field selection, derived relationships, numeric precision, constants, and recommended error-handling and QA/validation workflows.
  - Includes examples, checklists, and guidance on using the Effect API for external calls during migrations.
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
