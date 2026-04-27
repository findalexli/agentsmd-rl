# docs: bun-types changes don't require `bun bd`

Source: [oven-sh/bun#29098](https://github.com/oven-sh/bun/pull/29098)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Adds a short section to CLAUDE.md clarifying that edits to `packages/bun-types/**/*.d.ts` are type-only and don't need a native build — `bun-types.test.ts` just packs the declarations and runs `tsc` against fixtures, so it can be run with system Bun directly.

Prevents agents from kicking off a 30-min cold build to validate a `.d.ts` tweak.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
