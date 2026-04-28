# chore(devx): add CLAUDE.md and .claude/rules

Source: [kumahq/kuma#15642](https://github.com/kumahq/kuma/pull/15642)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/rules/debug.md`
- `.claude/rules/linting.md`
- `.claude/rules/policies.md`
- `.claude/rules/release.md`
- `.claude/rules/testing.md`
- `CLAUDE.md`

## What to add / change

## Motivation

About 3 months ago we agreed to add CLAUDE.md to the repo - I thought it was already pushed but apparently it wasn't. This adds it along with `.claude/rules/` for the modular bits.

## Implementation information

**CLAUDE.md** (136 lines) - project-level instructions for Claude Code:
- build/test/lint commands with focused-test variants
- architecture section with component relationships, not just a file tree
- 4 project-specific gotchas (RBAC gate, import aliases, cached resources, pkg/app boundary)
- commit format with examples, pre-commit workflow
- no generic advice, no README duplication, bullets over paragraphs throughout

**`.claude/rules/`** - keeps the root file under 150 lines by splitting detailed reference into topic files:
- `linting.md` - importas aliases, depguard blocklist, SafeSpanEnd requirement
- `testing.md` - Ginkgo suite structure, golden matchers, table tests, mock strategy
- `policies.md` - plugin directory layout (hand-written vs generated), spec markers, generation pipeline
- `release.md` - branch/tag format, release steps, utility commands
- `debug.md` - k3d cluster setup, Envoy admin API, skaffold dev loop, common debugging tasks

> Changelog: skip

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
