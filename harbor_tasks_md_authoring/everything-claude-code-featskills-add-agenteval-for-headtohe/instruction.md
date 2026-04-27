# feat(skills): add agent-eval for head-to-head coding agent comparison

Source: [affaan-m/everything-claude-code#540](https://github.com/affaan-m/everything-claude-code/pull/540)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/agent-eval/SKILL.md`

## What to add / change

## Summary

Adds `agent-eval` as a skill — a lightweight CLI tool for comparing coding agents (Claude Code, Aider, Codex, etc.) head-to-head on custom tasks using YAML task definitions, git worktree isolation, and deterministic + model-based judges.

## Type
- [x] Skill
- [ ] Agent
- [ ] Hook
- [ ] Command

## What it covers
- YAML task definitions with judge criteria (pytest, grep, LLM-as-judge)
- Git worktree isolation per run (no Docker needed)
- Metrics: pass rate, cost, time, consistency (pass@k)
- Comparison report generation

## Testing
- Tested with Claude Code locally
- 39 tests passing in the [agent-eval repo](https://github.com/joaquinhuigomez/agent-eval)
- Follows SKILL.md template format

## Checklist
- [x] Follows format guidelines
- [x] Tested with Claude Code
- [x] No sensitive info (API keys, paths)
- [x] Clear descriptions

<!-- This is an auto-generated description by cubic. -->
---
## Summary by cubic
Adds the `agent-eval` skill, a lightweight CLI to compare coding agents on reproducible tasks and report pass rate, cost, time, and consistency. Helps teams make data-backed choices and run regressions on their own codebases.

- **New Features**
  - Adds `skills/agent-eval/SKILL.md` with activation steps, pinned `pip` install to a commit, workflow, and examples.
  - Declarative task YAML with judges (tests/commands, pattern checks, model-based review) and a `commit` pin for reproducibility.
  - Per-run git worktree reproducibility isolation (no Docker).
  - C

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
