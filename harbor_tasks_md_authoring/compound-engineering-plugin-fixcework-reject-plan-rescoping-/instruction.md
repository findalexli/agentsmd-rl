# fix(ce-work): reject plan re-scoping into human-time phases

Source: [EveryInc/compound-engineering-plugin#600](https://github.com/EveryInc/compound-engineering-plugin/pull/600)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/ce-work-beta/SKILL.md`
- `plugins/compound-engineering/skills/ce-work/SKILL.md`

## What to add / change

`/ce-work` no longer invents human-time estimates or proposes multi-day "session scope" breakdowns when it sees a plan with several implementation units. The skill already has the right tool for plan size (subagent dispatch in Phase 1 Step 4) and the right tool for plans that are genuinely too large (Phase 0's Large routing back to `/ce-brainstorm` or `/ce-plan`); it was reaching past both to borrow a human IC's framing that doesn't apply to agent execution.

Two changes, synced between `ce-work` and `ce-work-beta`:

- **Phase 1 Step 1** — the vague `Get user approval to proceed` bullet now only asks for approval when clarifying questions were needed. Plan scope is the plan's authority, not something to renegotiate at the start of execution.
- **Common Pitfalls** — explicit anti-pattern added: don't estimate human-hours per unit, don't propose phased sessions, don't ask the user to pick a subset of units. Points at the existing levers (subagent dispatch, Phase 0 Large routing) that already solve the real concern.

---

[![Compound Engineering](https://img.shields.io/badge/Built_with-Compound_Engineering-6366f1)](https://github.com/EveryInc/compound-engineering-plugin)
![Claude Code](https://img.shields.io/badge/Opus_4.7_(1M)-D97757?logo=claude&logoColor=white)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
