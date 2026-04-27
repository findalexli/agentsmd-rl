# Add CLAUDE.md

Source: [e2b-dev/E2B#1137](https://github.com/e2b-dev/E2B/pull/1137)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

<!-- CURSOR_SUMMARY -->
> [!NOTE]
> **Low Risk**
> Documentation-only change with no runtime or behavioral impact.
> 
> **Overview**
> Adds `CLAUDE.md` with contributor workflow notes: preferred dependency managers (pnpm/poetry), required formatting/lint/typecheck steps, how to run tests, how to regenerate the API client (`make codegen`), and where default credentials are stored.
> 
> <sup>Written by [Cursor Bugbot](https://cursor.com/dashboard?tab=bugbot) for commit b1c2f5a07871b7577f806f45ce3a52829b40fdd0. This will update automatically on new commits. Configure [here](https://cursor.com/dashboard?tab=bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
