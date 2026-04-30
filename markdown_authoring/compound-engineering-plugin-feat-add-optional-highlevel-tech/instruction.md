# feat: add optional high-level technical design to plan-beta skills

Source: [EveryInc/compound-engineering-plugin#322](https://github.com/EveryInc/compound-engineering-plugin/pull/322)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/ce-plan-beta/SKILL.md`
- `plugins/compound-engineering/skills/deepen-plan-beta/SKILL.md`

## What to add / change

## Summary

Technical plans are often valuable when they include pseudo-code, DSL grammars, or architectural diagrams in plans to validate the approach direction — without the plan crossing into prescriptive implementation code that downstream implementing agents take as gospel.

This PR adds optional "High-Level Technical Design" support at two levels:

- **Overview level** (new plan section before Implementation Units): system-level shape — architecture diagrams, DSL grammars, state machines, data flow sketches. The skill chooses the right medium based on what the work actually involves.
- **Unit level** (new optional field per implementation unit): tactical shape of a specific component, only when prose alone would leave the approach ambiguous.

Both levels carry explicit non-prescriptive framing: *"This is directional guidance for review, not implementation specification."*

Ultimately this paves a nice path to promote this to stable sometime soon.

### Why this matters

There's a gap between "decisions, not code" (current plan-beta) and literal implementation code. Pseudo-code/DSL sketches sit in that gap — they let a reviewer say "yes, this direction is right" without dictating what the implementing agent should produce. The key concern driving the design: avoid specific code that the next implementation agent takes as gospel and reproduces verbatim.

### Changes

**ce-plan-beta:**
- Soften core principle to allow pseudo-code/DSL sketches with non-pr

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
