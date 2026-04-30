# chore: add agents.md

Source: [windmill-labs/windmill#8849](https://github.com/windmill-labs/windmill/pull/8849)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

<!-- This is an auto-generated description by cubic. -->
## Summary by cubic
Add `AGENTS.md` to centralize agent workflow, dev setup, navigation tips, and banned Svelte patterns. Update `CLAUDE.md` to point to the new doc to avoid duplication and drift.

- **Refactors**
  - Added `AGENTS.md` covering workflow, validation/docs links, dev environment, banned `$bindable` on optional props (with alternatives), `wm-ts-nav` usage/limits, and core principles.
  - Replaced `CLAUDE.md` content with a single pointer to `AGENTS.md` to dedupe guidance.

<sup>Written for commit 91e0838d61f82879ef6bd6489aca1615d38f1c03. Summary will update on new commits.</sup>

<!-- End of auto-generated description by cubic. -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
