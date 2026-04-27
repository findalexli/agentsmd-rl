# feat(ce-brainstorm): probe rigor gaps with prose before Phase 2

Source: [EveryInc/compound-engineering-plugin#677](https://github.com/EveryInc/compound-engineering-plugin/pull/677)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/ce-brainstorm/SKILL.md`

## What to add / change

`ce-brainstorm` used to drift into solution-shape narrowing without pressure-testing the user's implicit framing. The agent's preambles would surface evidence-adjacent concerns ("no captive user", "teams is doing hidden work") but every question still defaulted to the blocking question tool's option format, which biases toward narrowing and lets the user pick from the agent's menu rather than produce a real observation.

Phase 1.2 now describes 5 shape-based rigor gaps as agent-internal lenses: evidence, specificity, counterfactual, attachment at Standard+, plus durability at Deep-product. Each describes a kind of gap in the user's opening rather than a keyword to pattern-match, so the agent reasons about presence instead of matching triggers.

Phase 1.3 adds a rule that each scope-appropriate gap must surface as a separate prose probe before Phase 2, not a 4-option menu. The rule ties to Interaction Rule 5(b): a menu signals which kinds of evidence count, where prose forces the user to produce content or surface their uncertainty. Per-gap examples are included, plus a trap flag on attachment so it fires whether or not a product shape has emerged through narrowing (the most common way the attachment probe gets missed). Genuine uncertainty ("no evidence yet") is recorded as an explicit assumption in the requirements doc rather than skipping the probe.

Verified across 2 interactive scenarios: a Deep-product brainstorm with no observed evidence produces clean 5/5 gap coverage i

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
