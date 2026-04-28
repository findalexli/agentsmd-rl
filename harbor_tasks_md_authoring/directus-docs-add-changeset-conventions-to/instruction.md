# docs: add changeset conventions to AGENTS.md

Source: [directus/directus#26547](https://github.com/directus/directus/pull/26547)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Added comprehensive guidance on creating and writing changesets:
- Command: `pnpm changeset`
- Past tense requirement for descriptions with examples
- Versioning guidelines (major/minor/patch)
- Breaking changes documentation format

Fixes #26546

Generated with [Claude Code](https://claude.ai/code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
