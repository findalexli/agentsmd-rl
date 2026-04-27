# feat(skill-design): document skill file isolation and platform variable constraints

Source: [EveryInc/compound-engineering-plugin#469](https://github.com/EveryInc/compound-engineering-plugin/pull/469)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary

- **File References in Skills** — documents that skills are self-contained directory units. Cross-directory (`../`) and absolute path references break at runtime, during plugin marketplace installation, and during cross-platform conversion.
- **Platform-Specific Variables in Skills** — platform-specific variables (Claude Code's `${CLAUDE_PLUGIN_ROOT}`, Codex's `CODEX_SANDBOX`, etc.) must not be used without graceful fallbacks. Prefer relative paths; use pre-resolution with explicit fallback when unavoidable.

Backed by official Claude Code docs and known issues:
- https://github.com/anthropics/claude-code/issues/11011
- https://github.com/anthropics/claude-code/issues/17741
- https://github.com/anthropics/claude-code/issues/12541

## Test plan

- [ ] Read the two new sections in AGENTS.md for clarity and accuracy
- [ ] Verify `bun run release:validate` still passes
- [ ] Confirm no conflicts with existing plugin-level AGENTS.md guidance

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
