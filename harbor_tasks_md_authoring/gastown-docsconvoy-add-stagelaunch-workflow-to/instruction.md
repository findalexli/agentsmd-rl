# docs(convoy): add stage-launch workflow to convoy SKILL.md

Source: [gastownhall/gastown#1878](https://github.com/gastownhall/gastown/pull/1878)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `docs/skills/convoy/SKILL.md`

## What to add / change

## Summary

Documents the `gt convoy stage` and `gt convoy launch` commands (implemented in #1820) in the convoy SKILL.md — the operational reference used by crews, polecats, and agents working with the convoy system.

- Updated architecture diagram to show stage-launch as a third creation path alongside batch sling and explicit create
- Added CLI quick-reference for `stage` and `launch` subcommands with all flags
- Added full **Stage-launch workflow** section covering:
  - Input types (epic ID, task list, convoy ID)
  - 13-step processing pipeline
  - Wave computation via Kahn's algorithm (slingable types, execution edges, deterministic ordering)
  - Convoy status model (4 statuses, valid transition matrix)
  - Error vs warning classification with categories and triggers
  - Launch behavior and dispatch semantics
  - Staged convoy daemon safety (`isConvoyStaged` guard, stranded scan exclusion)
  - Re-staging behavior
- Added stage-launch test commands and 9 new key test invariants
- Added reference to `docs/design/convoy/stage-launch/testing.md` (105 tests)
- Added 6 new common pitfalls for stage-launch
- Added `convoy_stage.go` and `convoy_launch.go` to key source files table
- Updated feed path descriptions noting staged convoy skipping

## Test plan

- [ ] Verify SKILL.md renders correctly in GitHub markdown preview
- [ ] Verify all referenced PRs (#1759, #1820) and file paths are valid
- [ ] Verify CLI examples match actual command signatures in `convoy_stage.go` and `co

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
