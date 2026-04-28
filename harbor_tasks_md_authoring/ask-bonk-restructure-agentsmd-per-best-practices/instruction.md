# Restructure AGENTS.md per best practices

Source: [ask-bonk/ask-bonk#108](https://github.com/ask-bonk/ask-bonk/pull/108)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Self-Review

Here's a summary of the changes and my self-review:

### Structural Changes (per best practices)

1. **Commands moved to the top** -- Per GitHub's analysis of 2,500+ AGENTS.md files, executable commands should be early since agents reference them constantly. Previously buried below Architecture.

2. **Added Rules section with Always/Never boundaries** -- This is the single most impactful section per best practices research. The old file scattered these rules across Logging/Security, Error Handling, and Testing. Now they're consolidated upfront:
   - **Always**: tsc+test before done, structured logging, Result types, errorWithException, type imports, import grouping
   - **Never**: logging secrets, adding deps without justification, Node.js APIs, mock-heavy tests, raw console

3. **Added full Project Structure** -- The old file had a "Key Files" list with only 9 `src/` files, missing `images.ts`, `metrics.ts`, `errors.ts`, `constants.ts`, and `hbs.d.ts`. The new version includes all 14 source files plus the `github/`, `cli/`, `test/`, and `ae_queries/` directories that were completely undocumented.

4. **Added Error Handling section with code example** -- The `Result`/`TaggedError` pattern is core to the codebase but was absent. The old file only said "Use try/catch for async operations" which doesn't reflect the actual `better-result` pattern used throughout.

5. **Consolidated and tightened** -- Removed redundancy (dependency management was duplicated as both

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
