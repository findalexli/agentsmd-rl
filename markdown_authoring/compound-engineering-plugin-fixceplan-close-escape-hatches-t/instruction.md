# fix(ce-plan): close escape hatches that let the skill abandon direct invocations

Source: [EveryInc/compound-engineering-plugin#554](https://github.com/EveryInc/compound-engineering-plugin/pull/554)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/ce-plan/SKILL.md`

## What to add / change

## Summary

ce:plan had interpretive gaps that let the agent classify legitimate planning requests as "not a planning task" and abandon the workflow, even on explicit `/ce:plan` invocations. This closes those escape hatches and adds smarter routing when planning isn't the right tool.

## What changed

**Closed escape hatches (commit 1):**

- Removed the "prefer ce:brainstorm first" sentence from the description frontmatter. It was meant for auto-selection routing but gave the model justification to reroute on direct invocation too.
- Added a top-of-body directive: "When directly invoked, always plan." with explicit instruction to never abandon. This is the primary fix.
- Replaced the dead-end "Do not proceed until you have a clear planning input" with actionable alternatives: ask clarifying questions or use Phase 0.4's bootstrap.
- Scoped the Phase 0.1b "everything else" exit clause (quick questions, factual lookups) to auto-selection only.
- Broadened Phase 0.4 from "No-Requirements-Doc Fallback" to "Planning Bootstrap" so it covers any underspecified input.

**Smart routing after bootstrap (commit 2):**

After Phase 0.4's bootstrap establishes enough context, ce:plan now detects two cases where a different workflow fits better:

- **Symptom without root cause** (broken behavior, cause unknown): auto-routes to `ce:debug` with announcement. Can't plan a fix for something you haven't diagnosed.
- **Clear task ready to execute** (known fix, no decisions to make): suggests `ce:w

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
