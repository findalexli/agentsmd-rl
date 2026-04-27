# Add weekly statusline cache-check task to running-tend skill

Source: [max-sixty/worktrunk#2211](https://github.com/max-sixty/worktrunk/pull/2211)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/running-tend/SKILL.md`

## What to add / change

Captures the `wt-perf cache-check` workflow as a weekly maintenance task in the `running-tend` skill, alongside the existing MSRV bump.

The render of `wt list statusline --claude-code` runs on every Claude Code prompt redraw, so any new in-process cache-miss duplicate there compounds into measurable fseventsd / IPC load — worth catching weekly rather than waiting for someone to notice the macOS daemon pegged at 100% CPU.

Includes the exact `RUST_LOG=debug … | grep wt-trace | wt-perf cache-check` invocation with a stdin-JSON stub, triage guidance for distinguishing legitimate distinct calls from real cache misses (with the `merge_base` / `worktree_at` precedents from PR #2209), and a 29-subprocess clean-tree baseline so a jump above ~32 is visible.

> _This was written by Claude Code on behalf of @max-sixty_

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
