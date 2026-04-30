#  feat: add the Codex version of formula-derivation.

Source: [wanshuiyin/Auto-claude-code-research-in-sleep#52](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/pull/52)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/skills-codex/formula-derivation/SKILL.md`

## What to add / change

Add the Codex version of formula-derivation.

  This skill is intended for research-style formula development before strict theorem proving:
  - choose the right invariant object
  - organize assumptions and notation
  - turn scattered equations into a coherent derivation line
  - separate identities, propositions, approximations, and remarks

  Recommended workflow:
  formula-derivation -> proof-writer

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
