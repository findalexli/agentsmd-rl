# docs: tighten tdd workflow red-green validation

Source: [affaan-m/everything-claude-code#896](https://github.com/affaan-m/everything-claude-code/pull/896)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/tdd-workflow/SKILL.md`

## What to add / change

## Why

In practice, the current `tdd-workflow` wording still leaves room for ambiguous behavior:
- moving into implementation before RED is actually validated
- treating unrelated build/setup failures as valid RED
- not making it clear that compile-time RED can be legitimate when a new test first instantiates buggy code

## What Changed

- require a validated RED before modifying production code
- clarify that RED must come from the intended bug, not unrelated setup/regression issues
- explicitly allow compile-time RED when a new test first exposes the buggy code path
- document a compact Git checkpoint flow: `test + RED`, `fix + GREEN`, optional `refactor`

<!-- This is an auto-generated description by cubic. -->
---
## Summary by cubic
Refines the TDD workflow docs to require a validated RED before any production changes, with clear runtime vs compile-time criteria and guards against unrelated failures. Adds a Git checkpoint flow with commit-after-RED and defer-fix-until-GREEN rules, scoped to commits on the current active branch and reachable from HEAD, no squashing until complete, plus compact message templates that capture evidence; separate evidence-only commits aren’t needed when RED/GREEN is shown.

<sup>Written for commit 9cc5d085e13b31a07d5c95a7ba31ba8174f648f0. Summary will update on new commits.</sup>

<!-- End of auto-generated description by cubic. -->

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRab

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
