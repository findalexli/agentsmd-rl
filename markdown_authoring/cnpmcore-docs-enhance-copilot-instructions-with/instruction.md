# docs: Enhance Copilot instructions with DDD architecture

Source: [cnpm/cnpmcore#838](https://github.com/cnpm/cnpmcore/pull/838)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

## Overview

This PR significantly enhances the `.github/copilot-instructions.md` file to provide comprehensive guidance for GitHub Copilot when assisting with cnpmcore development. The instructions have been expanded from 281 lines to 564 lines, adding critical sections that align with GitHub's best practices for coding agents.

## What Changed

### New Sections Added

**1. Code Style and Conventions**
- Detailed Oxlint and Prettier configuration rules
- TypeScript conventions (strict typing, avoiding `any`, ES modules)
- Testing conventions with naming patterns and mock usage
- Complete code examples for test structure

**2. Domain-Driven Design (DDD) Architecture**
- Visual layer architecture showing dependency flow
- Detailed responsibilities for each layer:
  - Controller: HTTP interface, validation, authentication
  - Service: Business logic orchestration
  - Repository: Data access and persistence
  - Entity: Domain models with business behavior
  - Model: ORM definitions
- Repository method naming conventions (`findX`, `saveX`, `removeX`, `listXs`)
- Request validation trilogy workflow (params → auth → authorization)
- Database model modification guidelines (update all 3 locations)

**3. Infrastructure Adapters**
- Documentation of enterprise customization points
- Adapter types: NFSClientAdapter, QueueAdapter, AuthAdapter, BinaryAdapter

**4. Semantic Commit Messages**
- Conventional commit format standards
- Real-world examples for feat, fix, docs, chore, test, refa

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
