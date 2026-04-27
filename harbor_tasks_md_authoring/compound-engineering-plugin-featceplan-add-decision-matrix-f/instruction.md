# feat(ce-plan): add decision matrix form, unchanged invariants, and risk table format

Source: [EveryInc/compound-engineering-plugin#417](https://github.com/EveryInc/compound-engineering-plugin/pull/417)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/ce-plan/SKILL.md`

## What to add / change

Three targeted improvements to the ce:plan template, informed by analyzing well-crafted external plan specs and identifying patterns that genuinely strengthen our output.

**Decision matrix as a named design form** — The section 3.4 table (High-Level Technical Design) lists pseudo-code, diagrams, flowcharts, etc. but didn't name decision/behavior matrices. For work involving flag combinations or multi-input behavior, a compact inputs-to-outcomes table is the clearest communication form. Two independent external specs both used this pattern unprompted.

**Unchanged invariants in System-Wide Impact** — The template already asks "what may be affected" but never prompts for the inverse: what explicitly doesn't change. When a plan touches shared surfaces, listing unchanged APIs and behaviors gives reviewers blast-radius assurance that Scope Boundaries (deliberate non-goals) doesn't cover. Added as an optional bullet in the existing section.

**Risk | Mitigation table format** — Changed from loose bullets (`- [risk]`) to a table that forces pairing each risk with how it's addressed. The core template uses a 2-column table; the Deep plan extension uses a 4-column table adding Likelihood and Impact. Prevents orphaned risks without mitigation plans.

## Test plan

- [x] `bun test` passes (497 tests, 0 failures)
- Template changes are in markdown fenced blocks — no parser or converter impact

---

[![Compound Engineering v2.55.0](https://img.shields.io/badge/Compound_Engineering-v2.55.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
