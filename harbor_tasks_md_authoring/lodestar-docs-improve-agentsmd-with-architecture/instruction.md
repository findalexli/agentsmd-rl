# docs: improve AGENTS.md with architecture patterns and pitfalls

Source: [ChainSafe/lodestar#8929](https://github.com/ChainSafe/lodestar/pull/8929)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## What

Improves the project `AGENTS.md` with practical knowledge gained from working with the codebase. This helps AI coding tools (Codex CLI, Claude Code, etc.) produce better code by understanding Lodestar's patterns and avoiding common mistakes.

## Changes

### New sections
- **Architecture patterns**: fork guards (`isForkPostX`), `ChainForkConfig`, state access, SSZ value vs view types, fork choice caching gotcha, typed error handling, structured logging
- **Common pitfalls**: lint before push, `lib/` vs `src/`, stale fork choice head, holding state references, missing `.js` extensions, force pushing after review
- **Adding a new API endpoint**: route → codecs → handler → tests workflow

### Improvements to existing sections
- **Build commands**: added per-package `--filter` builds and `--project unit` vitest filter
- **Code style**: documented named exports convention
- **Testing**: expanded with vitest project filters and examples
- **PR guidelines**: added package-scoped commit examples, respond to bot reviewers, reply in-thread
- **Error handling**: moved from "style learnings" into architecture section with fuller typed error pattern

### Removed
- Duplicate error handling snippet (consolidated into architecture section)

> 🤖 This PR was authored by Lodekeeper with AI assistance.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
