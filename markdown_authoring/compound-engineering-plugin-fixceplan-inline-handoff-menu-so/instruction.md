# fix(ce-plan): inline handoff menu so post-plan options are never skipped

Source: [EveryInc/compound-engineering-plugin#615](https://github.com/EveryInc/compound-engineering-plugin/pull/615)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/ce-plan/SKILL.md`

## What to add / change

## Summary

Agents running `ce-plan` could write the plan file, offer to start `/ce-work` in prose, and stop, skipping the blocking post-generation menu that should gate the handoff. This PR restructures the final phase so the menu cannot be missed.

## What was happening

`SKILL.md` deferred both the trigger action (present the menu) and the branching logic (issue creation, Proof HITL flow) to `references/plan-handoff.md`. The confidence-check "passed" exit in 5.3.2 pointed to Phase 5.3.8 by section number. The 5.3.8 to 5.4 stub in turn said, in passive voice, "read this reference file when reaching this phase." The skill then ended with `NEVER CODE! Research, decide, and write the plan.`, which reads as a terminal completion admonition.

On the common path where the confidence check passed and no deepening was needed, the agent never re-entered the skill body at 5.3.8, never loaded the reference, and treated writing the plan as the final act.

## Fix

- The 5.3.2 exit is now imperative: `load references/plan-handoff.md now and execute 5.3.8, 5.3.9, 5.4 in sequence`. The load is the instruction, not a section signpost.
- The 5.3.8 to 5.4 stub now inlines the menu question and its 4 options directly in `SKILL.md`. Branching (issue creation, Proof HITL, post-HITL resync) stays in the reference.
- A new **Completion check** at the terminal position tells the agent it is not done until the menu has been presented.
- `NEVER CODE` moves to Phase 4, where implementation temptation 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
