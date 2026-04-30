# chore: add Cypress E2E automation rules for Cursor and Claude

Source: [safe-global/safe-wallet-monorepo#7070](https://github.com/safe-global/safe-wallet-monorepo/pull/7070)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/cypress-e2e.mdc`
- `AGENTS.md`

## What to add / change

## Summary

This PR adds comprehensive Cypress E2E test automation rules that will be automatically applied by both Cursor and Claude when working on Cypress test files.

## Changes

- **Added** `.cursor/rules/cypress-e2e.mdc` - Comprehensive Cypress E2E automation rules with:
  - Test structure and naming conventions ("Verify that" format)
  - Page Object Model (POM) patterns
  - Element selection strategies (data-testid preferred)
  - Function organization and reusability guidelines
  - Helper function placement rules
  - Test organization patterns
  - Data management best practices
  - Error handling strategies
  - Copilot-specific patterns

- **Updated** `AGENTS.md` - Added reference to the new Cypress rules file in the E2E Tests section

## How It Works

- **Cursor**: Automatically loads the rules when editing `**/cypress/**/*.cy.js` or `**/cypress/**/*.pages.js` files via glob patterns
- **Claude**: Reads the rules file when referenced in AGENTS.md

## Benefits

- Single source of truth for Cypress test guidelines
- Automatic application when working on Cypress files
- Consistent test structure and patterns across the codebase
- Clear guidance on function placement and reusability
- Better maintainability through standardized practices

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> **Low Risk**
> Documentation/rules-only change that doesn’t alter runtime code or test execution, but may influence future test contributions via stricter conventions.
> 
> **Overview**
> Adds a n

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
