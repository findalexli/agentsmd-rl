# fix(ce-compound): stack-aware reviewer routing and remove phantom agents

Source: [EveryInc/compound-engineering-plugin#497](https://github.com/EveryInc/compound-engineering-plugin/pull/497)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/ce-compound/SKILL.md`

## What to add / change

## Summary

- **Stack-aware kieran reviewer selection**: Phase 3 routing no longer hardcodes `kieran-rails-reviewer` for all code-heavy issues. It now selects the reviewer matching the repo's primary stack (Rails, Python, or TypeScript), with `code-simplicity-reviewer` always running regardless of stack.
- **Remove phantom agent references**: `cora-test-reviewer` (listed since initial commit, Oct 2025) and `every-style-editor` never existed as agent files — removed all references.
- **Fully-qualified agent names**: All agent references in the skill now use the `compound-engineering:<category>:<agent-name>` namespace per AGENTS.md convention.

Closes #491

## Test plan

- [ ] Verify Phase 3 routing instructions are unambiguous — `code-simplicity-reviewer` always runs, kieran reviewer is additive
- [ ] Confirm no remaining references to `cora-test-reviewer` or `every-style-editor` in the plugin
- [ ] Confirm all agent references use fully-qualified names
- [ ] Run `bun run release:validate` to check plugin consistency

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
