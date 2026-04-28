# docs: add AGENTS.md

Source: [playcanvas/editor#1734](https://github.com/playcanvas/editor/pull/1734)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary

- Adds `AGENTS.md` documenting conventions, architecture, and best practices for AI agents and developers working on the editor frontend.
- Covers project overview, page loading lifecycle, directory structure, the Caller pattern, editor-api module, build system, testing, code style, common patterns, and anti-patterns.

## Details

This is a documentation-only change — no code modifications. The file serves as a reference for both human contributors and AI coding agents to understand how the editor is structured and how to make changes correctly.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
