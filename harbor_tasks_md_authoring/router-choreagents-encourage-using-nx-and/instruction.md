# chore(agents): encourage using nx and pnpm instead of direct execution, add instruction for sandboxed execution

Source: [TanStack/router#6671](https://github.com/TanStack/router/pull/6671)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

This change is for internal development only, no impact on the packages

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Documentation**
  * Updated development workflow documentation to use pnpm nx commands instead of npx nx for testing, package management, and workspace operations.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
