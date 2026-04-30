# chore: consolidate agent instructions and remove Cursor rules

Source: [formbricks/formbricks#7096](https://github.com/formbricks/formbricks/pull/7096)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/build-and-deployment.mdc`
- `.cursor/rules/cache-optimization.mdc`
- `.cursor/rules/database-performance.mdc`
- `.cursor/rules/database.mdc`
- `.cursor/rules/documentations.mdc`
- `.cursor/rules/formbricks-architecture.mdc`
- `.cursor/rules/github-actions-security.mdc`
- `.cursor/rules/i18n-management.mdc`
- `.cursor/rules/react-context-patterns.mdc`
- `.cursor/rules/review-and-refine.mdc`
- `.cursor/rules/storybook-component-migration.mdc`
- `.cursor/rules/storybook-create-new-story.mdc`
- `AGENTS.md`

## What to add / change

## Summary
This PR consolidates all agent-specific instructions into the `AGENTS.md` file and removes individual `.cursor/rules/*.mdc` files. 

### Key Changes
- **Single Source of Truth:** Moved essential guidelines from various Cursor MDC rules into a single, comprehensive `AGENTS.md` file.
- **Context Optimization:** Deleting the individual MDC rules reduces the context window bloat for AI agents, potentially lowering costs and improving response quality.
- **Improved Maintainability:** Having one file (`AGENTS.md`) makes it easier to keep instructions up to date across different AI agents (Cursor, PR reviewers, etc.).
- **New Guidelines:** Added specific instructions for i18n workflows (Lingo.dev), database multi-tenancy, and a note about SonarQube usage.

## Test plan
- Verified that `AGENTS.md` contains the moved information.
- Confirmed that the MDC rules have been deleted.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
