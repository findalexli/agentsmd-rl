# docs: add Cursor rules for RTK Query, Redux slices, and Zod schemas

Source: [LedgerHQ/ledger-live#13939](https://github.com/LedgerHQ/ledger-live/pull/13939)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/redux-slice.mdc`
- `.cursor/rules/rtk-query-api.mdc`
- `.cursor/rules/zod-schemas.mdc`

## What to add / change

### ✅ Checklist

- [ ] `npx changeset` was attached.
- [x] **Covered by automatic tests.** _N/A - Documentation/Cursor rules only_
- [x] **Impact of the changes:**
      - Cursor AI guidance for RTK Query patterns
      - Cursor AI guidance for Redux slice patterns
      - Cursor AI guidance for Zod schema validation

### 📝 Description

**Problem**: Developers need consistent patterns when working with RTK Query, Redux slices, and Zod validation in the codebase.

**Solution**: Added three new Cursor rules to provide AI-assisted guidance:

- **`rtk-query-api.mdc`**: Best practices for `createApi` - endpoints, caching, tags (as enums), error handling, and API registration
- **`redux-slice.mdc`**: Best practices for `createSlice` - reducers, selectors, extraReducers, and slice registration
- **`zod-schemas.mdc`**: Patterns for Zod schema validation in `state-manager/types.ts` files

These rules follow existing patterns from `dada-client`, `cmc-client`, and other implementations in the codebase.

### ❓ Context

- **JIRA or GitHub link**: https://ledgerhq.atlassian.net/browse/LIVE-25641 - Internal tooling improvement

---

### 🧐 Checklist for the PR Reviewers

- **The code aligns with the requirements** described in the linked JIRA or GitHub issue.
- **The PR description clearly documents the changes** made and explains any technical trade-offs or design decisions.
- **There are no undocumented trade-offs**, technical debt, or maintainability issues.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
