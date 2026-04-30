# chore: add AGENTS.md symlink

Source: [jdx/mise#9094](https://github.com/jdx/mise/pull/9094)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary

- Add `AGENTS.md` as a symlink to `CLAUDE.md` so agent-oriented tooling can discover the existing repository instructions without duplicating them.

## Validation

- Commit hook passed: prettier, cargo-fmt, cargo-check, shellcheck, shfmt, pkl, taplo, lua-check, stylua, actionlint, markdownlint, schema.

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> **Low Risk**
> Low risk: adds a single documentation/discovery file and does not change runtime code or behavior.
> 
> **Overview**
> Adds `AGENTS.md` containing a reference to `CLAUDE.md` to make existing repository instructions discoverable to agent-oriented tooling without duplicating content.
> 
> <sup>Reviewed by [Cursor Bugbot](https://cursor.com/bugbot) for commit 0790b0f240a79a1c2f41ccb1828e51bb18edc37e. Bugbot is set up for automated code reviews on this repo. Configure [here](https://www.cursor.com/dashboard/bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
