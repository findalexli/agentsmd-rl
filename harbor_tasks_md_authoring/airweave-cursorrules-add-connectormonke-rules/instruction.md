# cursorrules: add connector+monke rules

Source: [airweave-ai/airweave#873](https://github.com/airweave-ai/airweave/pull/873)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/connector-development-end-to-end.mdc`
- `.cursor/rules/monke-testing-guide.mdc`
- `.cursor/rules/source-connector-implementation.mdc`
- `.cursor/rules/source-integration-rules.mdc`

## What to add / change

<!-- This is an auto-generated description by cubic. -->

## Summary by cubic
Adds comprehensive connector development and Monke E2E testing rules, replacing the old source integration guide. This clarifies end-to-end workflows and ensures nested entities like comments and files are verified.

- **New Features**
  - Added connector-development-end-to-end.mdc with step-by-step build and test workflow.
  - Added monke-testing-guide.mdc covering bongo, generation schemas/adapters, config, and full test flow (create, sync, verify, update, delete).
  - Added source-connector-implementation.mdc detailing entity schemas, token refresh, pagination, breadcrumbs, and file processing.

- **Refactors**
  - Removed source-integration-rules.mdc in favor of unified, clearer guides.
  - Standardized terminology and checklists; emphasized verification of all entity types.

<!-- End of auto-generated description by cubic. -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
