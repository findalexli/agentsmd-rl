# fix(ce-work,ce-work-beta): add safety checks for parallel subagent dispatch

Source: [EveryInc/compound-engineering-plugin#557](https://github.com/EveryInc/compound-engineering-plugin/pull/557)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/ce-work-beta/SKILL.md`
- `plugins/compound-engineering/skills/ce-work/SKILL.md`

## What to add / change

## Summary

- Adds a **Parallel Safety Check** gate that builds a file-to-unit mapping from plan metadata and auto-downgrades to serial subagents when file overlap is detected
- Parallel subagents no longer stage, commit, or run the full test suite -- the orchestrator handles all validation and commits after the entire batch completes
- Splits the after-completion workflow into distinct serial vs. parallel flows to prevent mixed-tree interference
- Propagates all changes to `ce-work-beta`

Addresses #550 (short-term mitigation for parallel dispatch safety without introducing worktree isolation).

## Context

Issue #550 correctly identifies that parallel subagents sharing a working directory risk git index contention, staging leaks, and test interference. The medium-term solution (worktree isolation) has complexity around nested worktrees (Conductor users already operate in worktrees) and merge-back orchestration.

This PR takes the short-term path: make parallel-without-isolation safe by (1) tightening the overlap detection from a vague heuristic to an explicit file-set intersection check, (2) removing git and test operations from parallel subagents entirely, and (3) having the orchestrator validate and commit sequentially after all parallel work completes.

## Changes

**Phase 1 Step 4 -- Choose Execution Strategy:**
- Strategy table now references the new Parallel Safety Check instead of "non-overlapping files"
- New **Parallel Safety Check** block: mandatory file-to-unit m

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
