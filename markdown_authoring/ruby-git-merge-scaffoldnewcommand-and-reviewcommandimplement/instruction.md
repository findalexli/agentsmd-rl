# Merge scaffold-new-command and review-command-implementation into command-implementation

Source: [ruby-git/ruby-git#1201](https://github.com/ruby-git/ruby-git/pull/1201)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/skills/command-implementation/REFERENCE.md`
- `.github/skills/command-implementation/SKILL.md`
- `.github/skills/command-test-conventions/SKILL.md`
- `.github/skills/command-yard-documentation/SKILL.md`
- `.github/skills/extract-command-from-lib/SKILL.md`
- `.github/skills/project-context/SKILL.md`
- `.github/skills/refactor-command-to-commandlineresult/SKILL.md`
- `.github/skills/review-arguments-dsl/CHECKLIST.md`
- `.github/skills/review-arguments-dsl/SKILL.md`
- `.github/skills/review-backward-compatibility/SKILL.md`
- `.github/skills/review-command-implementation/SKILL.md`
- `.github/skills/review-command-tests/SKILL.md`
- `.github/skills/review-cross-command-consistency/SKILL.md`
- `.github/skills/reviewing-skills/SKILL.md`

## What to add / change

## Summary

Consolidate two complementary skills (`scaffold-new-command` and `review-command-implementation`) into a single `command-implementation` skill that supports three modes: **scaffold**, **update**, and **review**.

The merged skill is split into two files to keep the orchestrator's context footprint small:

- **SKILL.md** (213 lines) — Input, Workflow, and Output sections. This is what the orchestrator loads.
- **REFERENCE.md** (791 lines) — detailed reference content loaded by subagents only during the workflow steps that need it.

## Changes

- **New**: `.github/skills/command-implementation/SKILL.md` — orchestrator-facing skill with three workflow modes
- **New**: `.github/skills/command-implementation/REFERENCE.md` — detailed reference extracted from the merged content
- **Deleted**: `.github/skills/scaffold-new-command/SKILL.md`
- **Deleted**: `.github/skills/review-command-implementation/SKILL.md`
- **Updated**: Cross-references in 11 skill files to point to the new location
- **Updated**: Git doc URLs simplified to `https://git-scm.com/docs/git-{command}` (always latest)

## Motivation

- The two old skills had significant overlap — both needed to understand the same architecture contract, command template, and DSL rules
- Having a single skill with modes eliminates duplication and ensures scaffold and review stay in sync
- The SKILL.md + REFERENCE.md split follows the pattern established by `review-arguments-dsl` (SKILL.md + CHECKLIST.md), keeping the orches

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
