# fix: use unique output filenames to prevent parallel agent collision

Source: [parcadei/Continuous-Claude-v3#102](https://github.com/parcadei/Continuous-Claude-v3/pull/102)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/agents/aegis.md`
- `.claude/agents/agentica-agent.md`
- `.claude/agents/arbiter.md`
- `.claude/agents/architect.md`
- `.claude/agents/atlas.md`
- `.claude/agents/braintrust-analyst.md`
- `.claude/agents/critic.md`
- `.claude/agents/debug-agent.md`
- `.claude/agents/herald.md`
- `.claude/agents/judge.md`
- `.claude/agents/kraken.md`
- `.claude/agents/liaison.md`
- `.claude/agents/maestro.md`
- `.claude/agents/oracle.md`
- `.claude/agents/pathfinder.md`
- `.claude/agents/phoenix.md`
- `.claude/agents/plan-agent.md`
- `.claude/agents/profiler.md`
- `.claude/agents/review-agent.md`
- `.claude/agents/scout.md`
- `.claude/agents/session-analyst.md`
- `.claude/agents/sleuth.md`
- `.claude/agents/spark.md`
- `.claude/agents/surveyor.md`
- `.claude/agents/validate-agent.md`

## What to add / change

## Summary

Fixes #96 - Agent output file collision in parallel execution.

When multiple agents of the same type run in parallel (e.g., 5 oracle agents researching different topics), they all wrote to the same hardcoded `latest-output.md` path, causing **complete data loss** for all but the last agent to finish.

## Changes

- Replace `latest-output.md` with `output-{timestamp}.md` in all 25 agent definitions
- Agents now generate unique filenames using Unix epoch timestamp
- Updated `maestro.md` to read most recent file: `ls -t output-*.md | head -1`

## Before/After

**Before:**
```
.claude/cache/agents/oracle/latest-output.md  ← all agents overwrite this
```

**After:**
```
.claude/cache/agents/oracle/output-1736842800.md  ← agent 1
.claude/cache/agents/oracle/output-1736842865.md  ← agent 2
.claude/cache/agents/oracle/output-1736842930.md  ← agent 3
```

## Test Plan

- [ ] Run multiple oracle agents in parallel, verify separate output files
- [ ] Verify maestro can read from most recent agent outputs
- [ ] Confirm backward compatibility (old `latest-output.md` files still readable)

---

🤖 Generated with [Claude Code](https://claude.ai/code)

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> Prevents parallel agent output collisions by switching to unique, timestamped filenames and adjusting orchestration to consume the latest outputs.
> 
> - All agent docs now write to `$CLAUDE_PROJECT_DIR/.claude/cache/agents/<agent>/output-{timestamp}.md` instead of `latest-output.md`
> - `ma

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
