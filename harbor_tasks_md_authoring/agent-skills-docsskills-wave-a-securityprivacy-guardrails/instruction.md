# docs(skills): Wave A security/privacy guardrails

Source: [jdrhyne/agent-skills#16](https://github.com/jdrhyne/agent-skills/pull/16)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `prompts/munger-observer/SKILL.md`
- `skills/context-recovery/SKILL.md`
- `skills/google-ads/SKILL.md`

## What to add / change

## Summary
Adds Security/Privacy addenda for Wave A skills:
- context-recovery
- google-ads
- munger-observer

## Changes
- Adds minimum-scope retrieval and consent language
- Clarifies explicit confirmation for mutating ad-account actions
- Adds privacy constraints for memory/session analysis

## Risk
Docs-only changes (no code/runtime behavior changes).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
