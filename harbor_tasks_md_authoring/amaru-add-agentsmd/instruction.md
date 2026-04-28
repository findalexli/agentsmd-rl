# add AGENTS.md

Source: [pragma-org/amaru#741](https://github.com/pragma-org/amaru/pull/741)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

This has been created by opencode /init and looks reasonable to me, but I don’t have experience with using this file.

Claude doesn’t yet reliably read AGENTS.md, so CLAUDE.md is a symlink to that (in order to keep one source of truth).

Signed-off-by: Roland Kuhn <rk@rkuhn.info>


<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Documentation**
  * Added comprehensive development guidelines documentation covering build, lint, and test command recommendations
  * Included detailed coding standards, style guidelines, and workflow instructions for developers
  * Added reference documentation for project conventions, testing practices, and best practices

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
