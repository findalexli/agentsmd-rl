# feat: additional improvements to cursorrules and claudemd

Source: [recallnet/js-recall#1233](https://github.com/recallnet/js-recall/pull/1233)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/api-specific-config.mdc`
- `.cursor/rules/org-general-practices.mdc`
- `.cursor/rules/org-typescript-standards.mdc`
- `.cursor/rules/repo-specific-config.mdc`
- `CLAUDE.md`

## What to add / change

## Summary
This PR significantly enhances our development documentation and AI agent guidance by adding comprehensive coding standards, patterns, and philosophy that were previously undocumented but are critical to our development practices.

## Changes

### Documentation Files Updated
- `.cursor/rules/api-specific-config.mdc` - API-specific standards
- `.cursor/rules/org-general-practices.mdc` - Organization-wide practices
- `.cursor/rules/repo-specific-config.mdc` - Repository configuration
- `CLAUDE.md` - AI agent guidance and code philosophy

### Key Additions

#### Database & Performance Standards
- **SQL-First Philosophy**: Documented preference for database computations over in-memory processing
- **Migration Best Practices**: Added Drizzle migration guidelines including rollback strategies
- **Database Type Safety**: Explicit rules for handling JSON fields, numeric types, and null values
- **Query Optimization**: Added requirements for indexes, pagination, and query performance

#### Testing Standards
- **Accurate Coverage Thresholds**: Updated to reflect actual requirements from `coverage.config.json`
  - Global: 46% functions (not 80% as previously undocumented)
  - Package-specific: 0% for apps, 100% for new packages
- **Coverage Migration Strategy**: Documented gradual improvement approach for legacy code

#### Code Quality Standards
- **Dead Code Prevention**: Added detection strategies and regular cleanup requirements
- **Pull Request 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
