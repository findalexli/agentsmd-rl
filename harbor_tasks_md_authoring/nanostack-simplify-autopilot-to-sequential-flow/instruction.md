# Simplify autopilot to sequential flow

Source: [garagon/nanostack#68](https://github.com/garagon/nanostack/pull/68)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plan/SKILL.md`
- `qa/SKILL.md`
- `review/SKILL.md`
- `security/SKILL.md`

## What to add / change

## Summary

Root cause of autopilot getting stuck: the parallel Agent tool call instructions were too complex for the agent to execute reliably. The agent got confused between "launch 3 parallel agents" and "proceed sequentially" and froze.

Reverted all 4 SKILL.md files to the simple sequential autopilot that worked in the world clock sprint: review → security → qa → ship, one at a time, with status messages between steps.

Parallel execution remains available via `/conductor` for multi-terminal setups.

## What changed

- plan/SKILL.md: removed parallel Agent tool call instructions, restored simple sequential flow
- review/SKILL.md: removed "parallel sub-agent" branching, restored direct next-skill flow
- security/SKILL.md: same
- qa/SKILL.md: same

## Test plan

- [x] No Agent tool call instructions in any SKILL.md autopilot section
- [x] Sequential flow: review → security → qa → ship
- [x] Stop conditions preserved (blocking issues, critical vulns, test failures)
- [x] Conductor reference preserved for parallel use case

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
