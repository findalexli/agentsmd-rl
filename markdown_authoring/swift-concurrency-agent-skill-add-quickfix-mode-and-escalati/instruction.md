# Add quick-fix mode and escalation guidance

Source: [AvdLee/Swift-Concurrency-Agent-Skill#18](https://github.com/AvdLee/Swift-Concurrency-Agent-Skill/pull/18)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `swift-concurrency/SKILL.md`

## What to add / change

## Summary

This PR folds my personal “swift-concurrency-expert” quick‑fix guidance into the main `swift-concurrency` skill so the agent can resolve simple diagnostics fast, and escalate only when needed.

## What changed

- Added **Quick Fix Mode** entry/exit criteria to explicitly gate when fast, minimal fixes are appropriate.
- Added a **Quick Fix Playbook** that maps common diagnostics to smallest safe fixes with escalation triggers.
- Added a clear **Escalation Path** for harder issues (build‑setting discovery → isolation re‑evaluation → decision tree).
- Added **Quick Fix verification** guidance to keep validation proportional to change size.

## Why this improves the skill

These updates add behavior‑level guidance the agent can act on (not just more prose):

- The agent can confidently do small, safe fixes without defaulting to deep dives.
- Diagnostics are mapped to concrete, low‑risk fixes with clear escalation triggers.
- The agent can scale up when needed while still validating quick fixes.

Net effect: faster resolution for simple issues, fewer over‑engineered responses, and a smoother transition to deeper research when complexity increases.

## Scope

Docs only (`swift-concurrency/SKILL.md`), no API or code changes.

## Testing

Not applicable (documentation change only).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
