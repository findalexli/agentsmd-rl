# Claude.md

Source: [lmnr-ai/lmnr#1239](https://github.com/lmnr-ai/lmnr/pull/1239)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

<!-- CURSOR_SUMMARY -->
> [!NOTE]
> **Low Risk**
> Documentation-only change adding a new guidance file; no runtime or behavioral impact.
> 
> **Overview**
> Adds a new `CLAUDE.md` with repository guidance for Claude Code, including monorepo structure, common dev commands for `frontend`/`app-server`/`query-engine`, local setup notes (required services and fallbacks), basic architecture diagram, migration workflow, and pre-commit hook behavior.
> 
> <sup>Written by [Cursor Bugbot](https://cursor.com/dashboard?tab=bugbot) for commit e8c45997e7c502642f40c2cb787068ddcb1e0af4. This will update automatically on new commits. Configure [here](https://cursor.com/dashboard?tab=bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
