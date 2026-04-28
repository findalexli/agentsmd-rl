# docs: fix turborepo → nx typo in AGENTS.md

Source: [LedgerHQ/ledger-live#16685](https://github.com/LedgerHQ/ledger-live/pull/16685)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

### 📝 Description

Fix a copy error in `AGENTS.md` — the monorepo description incorrectly referred to `turborepo` instead of `nx`.

**Change:**
> ~~This pnpm and turborepo monorepo provides frontend apps~~
> This pnpm and nx monorepo provides frontend apps

### ❓ Context

Caught post-merge on #16644.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
