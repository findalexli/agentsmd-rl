# Add agent skill: Vite dep optimizer debugging guide

Source: [withastro/astro#16066](https://github.com/withastro/astro/pull/16066)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/optimize-deps/SKILL.md`

## What to add / change

## Changes

- Adds a new agent skill at `.agents/skills/optimize-deps/SKILL.md` documenting tribal knowledge about Vite's dep optimizer as it applies to the Astro dev server.
- Covers how `optimizeDeps` works (scan phase vs bundle phase), why non-JS files like `.astro` require special handling, the roles of `vitefu`, `vite-plugin-environment`, and `astroFrontmatterScanPlugin`, and a debugging playbook with logging techniques and potential fix patterns.

## Testing

- No code changes — this is documentation/tooling only.

## Docs

- This IS the docs. No other changes needed.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
