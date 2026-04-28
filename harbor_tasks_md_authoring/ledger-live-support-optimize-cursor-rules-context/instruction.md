# support: optimize Cursor rules context usage

Source: [LedgerHQ/ledger-live#14352](https://github.com/LedgerHQ/ledger-live/pull/14352)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/client-ids.mdc`
- `.cursor/rules/cursor-rules.mdc`
- `.cursor/rules/git-workflow.mdc`
- `.cursor/rules/ldls.mdc`
- `.cursor/rules/react-general.mdc`
- `.cursor/rules/react-mvvm.mdc`
- `.cursor/rules/redux-slice.mdc`
- `.cursor/rules/rtk-query-api.mdc`
- `.cursor/rules/testing.mdc`
- `.cursor/rules/typescript.mdc`
- `.cursor/rules/zod-schemas.mdc`

## What to add / change

### ✅ Checklist

- [x] `npx changeset` was attached.
- [ ] **Covered by automatic tests.** _N/A — tooling config only, no runtime code changed._
- [x] **Impact of the changes:**
  - Cursor AI context window usage when working in this repo
  - No impact on build, CI, or runtime behavior

### 📝 Description

**Problem**: All 10 Cursor AI rules (`.cursor/rules/*.mdc`) had `alwaysApply: true`, injecting ~7,500–8,000 tokens of instructions into every conversation unconditionally — even when irrelevant (e.g., Lumen UI design tokens during a git operation, Zod schema patterns when editing a README).

**Solution**: Set `alwaysApply: false` on all rules so they activate conditionally via their existing `description` (agent-decided) and/or `globs` (file-matched) fields instead. All original descriptions and globs are preserved. Also adds missing YAML frontmatter to `client-ids.mdc` and a new `cursor-rules.mdc` authoring guide.

**How Cursor rule activation works** (from [the docs](https://cursor.com/docs/context/rules#rule-file-format)):

> If alwaysApply is true, the rule will be applied to every chat session. Otherwise, the description of the rule will be presented to the Cursor Agent to decide if it should be applied.

| Rule Type | Frontmatter | Behavior |
|---|---|---|
| Always Apply | `alwaysApply: true` | Injected into every conversation |
| Apply Intelligently | `description` + `alwaysApply: false` | Agent decides based on description |
| Apply to Specific 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
