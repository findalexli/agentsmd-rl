# feat(interview): add auto-confirm routing for high-confidence code answers (#357)

Source: [Q00/ouroboros#382](https://github.com/Q00/ouroboros/pull/382)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/interview/SKILL.md`

## What to add / change

## Summary

- Split PATH 1 (Code Confirmation) into **PATH 1a** (auto-confirm) and **PATH 1b** (confirmation)
- PATH 1a: high-confidence facts from manifests/configs are sent to MCP immediately with `[from-code][auto-confirmed]` prefix, user sees a non-blocking notification
- PATH 1b: medium/low confidence answers preserve the existing confirmation-question flow
- Updated Dialectic Rhythm Guard to count auto-confirms toward the 3-consecutive limit
- Updated example session to demonstrate auto-confirm vs. confirmation routing

## Why this is needed

From team meeting (2026-04-10):
> "AI가 충분히 다 확정지울 수 있는 것도 많거든요. 그래서 보호성을 줄이는 건 좋은데..."

Currently PATH 1 always blocks on user confirmation, even for unambiguous facts like "What language is this project?" when `pyproject.toml` clearly states Python 3.12. This creates unnecessary friction and makes the tool feel "weak".

**The key insight**: auto-confirm also naturally reduces user-facing round-trips (the goal of #358 batch questions), because factual questions are resolved instantly. The user only sees questions that genuinely require their judgment.

## Design decisions

- **SKILL.md only, no MCP code changes**: The MCP server remains a pure question generator (Ouroboros P3 principle). Auto-confirm is a routing decision made by the main session, which has codebase access — the MCP does not.
- **Strict criteria for PATH 1a**: Only exact manifest/config matches qualify. Inferred answers go through PATH 1b with user confirmation.
- 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
