# Add proof-writer skill for rigorous theory proof drafting

Source: [wanshuiyin/Auto-claude-code-research-in-sleep#18](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/pull/18)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/proof-writer/SKILL.md`

## What to add / change

## Summary
Add a `proof-writer` skill for rigorous ML/AI theory proof drafting and refinement.

## What it does
- writes structured proof packages from theorem statements or proof sketches
- preserves theorem scope unless a real repair requires a scope change
- supports iterative refinement while keeping the proof artifact explicit

## Scope
This PR is intentionally limited to `proof-writer` and its follow-up refinements.
The proof reviewer and proof review loop are being kept separate for now.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
