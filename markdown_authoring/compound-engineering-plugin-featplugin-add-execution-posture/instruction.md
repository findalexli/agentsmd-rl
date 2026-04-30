# feat(plugin): add execution posture signaling to ce:plan-beta and ce:work

Source: [EveryInc/compound-engineering-plugin#309](https://github.com/EveryInc/compound-engineering-plugin/pull/309)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/ce-plan-beta/SKILL.md`
- `plugins/compound-engineering/skills/ce-work/SKILL.md`

## What to add / change

## Summary

- Add lightweight execution posture signaling to `ce:plan-beta` so plans can hint at test-first or characterization-first discipline without becoming execution scripts
- Update `ce:work` to read and honor those signals proportionally — no state machine, just guidance and guardrails

## Motivation

[PR #230](https://github.com/EveryInc/compound-engineering-plugin/pull/230) proposed a standalone TDD skill that would restructure plan implementation units into explicit RED/GREEN/REFACTOR substeps after the fact.

However, we recently shipped `ce:plan-beta` in [PR #272](https://github.com/EveryInc/compound-engineering-plugin/pull/272) which is an shift to a decision-first planning philosophy that explicitly avoids micro-step choreography that was in the original `ce:plan` skill. 

This makes the proposed TDD skill in #230 fundamentally incompatible with plan-beta skill: a standalone skill that expands plans into TDD substeps contradicts the principle that plans should capture decisions, not execution scripts.

This PR takes the alternative path. Instead of a separate skill that post-processes plans, execution posture becomes a native part of the plan→work pipeline:

- `ce:plan-beta` detects when TDD or characterization-first discipline is warranted and carries a one-line signal in the relevant implementation units
- `ce:work` reads that signal and adjusts its execution accordingly

This supersedes PR #230. The useful ideas from that PR (discipline gua

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
