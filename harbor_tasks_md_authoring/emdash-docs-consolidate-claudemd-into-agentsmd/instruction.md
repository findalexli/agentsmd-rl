# docs: consolidate CLAUDE.md into AGENTS.md

Source: [generalaction/emdash#1061](https://github.com/generalaction/emdash/pull/1061)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

## Summary

- Replaced the full contents of `CLAUDE.md` with a single `@AGENTS.md` reference, eliminating ~310 lines of duplicated documentation
- Expanded `AGENTS.md` to be the single source of truth for all project documentation, adding tech stack details, development commands, comprehensive architecture docs, guardrails, and pre-PR checklist
- Added `pnpm run format` to the `test_commands` list in the AGENTS.md frontmatter

## Motivation

`CLAUDE.md` and `AGENTS.md` contained largely overlapping content that could drift out of sync. This consolidates everything into `AGENTS.md` and has `CLAUDE.md` reference it via the `@` directive, ensuring a single source of truth.

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> **Low Risk**
> Documentation-only restructuring plus adding `pnpm run format` to the declared `test_commands`; no runtime code paths are affected.
> 
> **Overview**
> Consolidates agent/developer documentation into `AGENTS.md` and replaces `CLAUDE.md` with a single `@AGENTS.md` include reference to eliminate duplicated guidance.
> 
> Expands `AGENTS.md` with more complete project docs (tech stack, dev/testing commands, architecture notes, guardrails/checklists) and updates its frontmatter to include `pnpm run format` in `test_commands`.
> 
> <sup>Written by [Cursor Bugbot](https://cursor.com/dashboard?tab=bugbot) for commit 441a2bef6f21539d0958e0a27b6db2b92612b4d9. This will update automatically on new commits. Configure [here](https://cursor.com/dashboard?tab=bugbot).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
