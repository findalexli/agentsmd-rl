# fix(ce-work): codify worktree isolation for parallel subagent dispatch

Source: [EveryInc/compound-engineering-plugin#698](https://github.com/EveryInc/compound-engineering-plugin/pull/698)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/ce-work-beta/SKILL.md`
- `plugins/compound-engineering/skills/ce-work/SKILL.md`

## What to add / change

## Summary

- Phase 1 Step 4's parallel-subagent flow described shared-directory dispatch with reactive collision recovery; worktree isolation only happened when the model spontaneously chose `isolation: "worktree"` (an emergent Opus behavior, not a skill instruction).
- Direct subagent dispatch to use `isolation: "worktree"` and `run_in_background: true` on Claude Code's `Agent` tool, with a documented fallback for platforms without built-in worktree primitives (Codex `spawn_agent`, Pi `subagent`).
- Reframe the "Parallel subagent constraints" block as the shared-directory fallback (no commits, no test runs by subagents) and add a new worktree-aware post-batch flow that resolves overlap at merge time instead of via the discovered-collision cross-check.

Stable/beta sync: applied identically to `ce-work` and `ce-work-beta` — the parallel-subagent body is shared verbatim between them.

## Test plan

- [x] `bun run release:validate` — passes (no manifest drift; doc-only edits)
- [x] `bun test` — 939 pass, 0 fail
- [x] Diff is two-file, +36/-8, scoped to Phase 1 Step 4 of both `SKILL.md` files

There is no code-level regression test for skill behavioral instructions; the verification is editorial review of the new isolation directive and the worktree-mode post-batch flow.

Fixes #682

[![CE](https://img.shields.io/badge/Built_with-Compound_Engineering-6366f1)](https://github.com/EveryInc/compound-engineering-plugin)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
