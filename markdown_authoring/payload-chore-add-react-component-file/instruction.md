# chore: add React component file structure conventions to CLAUDE.md

Source: [payloadcms/payload#16125](https://github.com/payloadcms/payload/pull/16125)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary

Adds guidance to CLAUDE.md for React/SCSS file organization. Each component should have its own named folder with `index.tsx` and `index.scss` rather than multiple `ComponentName.tsx` files sharing a single `.scss` in one directory.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
