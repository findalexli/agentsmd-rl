# fix(skills): load deferred MCP tools before checking availability

Source: [Q00/ouroboros#127](https://github.com/Q00/ouroboros/pull/127)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/evaluate/SKILL.md`
- `skills/evolve/SKILL.md`
- `skills/interview/SKILL.md`
- `skills/run/SKILL.md`
- `skills/seed/SKILL.md`
- `skills/status/SKILL.md`
- `skills/unstuck/SKILL.md`

## What to add / change

## Summary

- All 7 skills with MCP Path A/B logic now explicitly load deferred tools via `ToolSearch` before deciding between MCP mode and fallback mode
- Fixes #126: skills always fell to Path B because Claude Code registers plugin MCP tools as deferred tools that aren't callable until fetched

## Problem

Claude Code registers plugin MCP tools as **deferred tools**. They appear in `<available-deferred-tools>` but aren't in the active tool set until loaded via `ToolSearch`. The SKILL.md files checked "if the MCP tool is available" without loading them first, so the AI always concluded the MCP server was unavailable — even when it was running with all 14 tools registered.

## Changes

Added a mandatory "Load MCP Tools" step to each affected skill before the Path A/B decision:

| Skill | MCP tool loaded |
|-------|----------------|
| `interview` | `ouroboros_interview` |
| `seed` | `ouroboros_generate_seed` |
| `evolve` | `ouroboros_evolve_step` |
| `evaluate` | `ouroboros_evaluate` |
| `status` | `ouroboros_session_status` |
| `unstuck` | `ouroboros_lateral_think` |
| `run` | `ouroboros_execute_seed` |

## Test plan

- [ ] Fresh Claude Code session → `ooo interview "test"` → should use Path A (MCP mode) instead of Path B
- [ ] Verify other skills (seed, run, evaluate, etc.) also use MCP mode
- [ ] Confirm fallback still works if MCP server is genuinely unavailable

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
