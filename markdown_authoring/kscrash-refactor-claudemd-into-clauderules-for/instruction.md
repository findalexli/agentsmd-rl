# Refactor CLAUDE.md into .claude/rules/ for path-scoped loading

Source: [kstenerud/KSCrash#789](https://github.com/kstenerud/KSCrash/pull/789)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/CLAUDE.md`
- `.claude/rules/api-stability.md`
- `.claude/rules/async-signal-safety.md`
- `.claude/rules/code-style.md`
- `.claude/rules/monitor-sidecars.md`
- `.claude/rules/monitors.md`
- `.claude/rules/packaging.md`
- `.claude/rules/run-id.md`
- `.claude/rules/threadcrumb.md`
- `CLAUDE.md`

## What to add / change

## Summary

- Splits the 488-line root `CLAUDE.md` into 8 modular files under `.claude/`
- Always-loaded context reduced to ~160 lines (~67% reduction)
- Subsystem docs (sidecars, threadcrumb, run ID, monitors, async-signal-safety) are now path-scoped and only load when editing matching files
- Deduplicated the Run ID section (was listed twice)
- Removed verbose sample outputs from build commands

## Test plan

- [x] `swift build` succeeds
- [ ] Verify Claude Code picks up `.claude/CLAUDE.md` and `.claude/rules/` correctly
- [ ] Verify path-scoped rules load when editing matching files

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
