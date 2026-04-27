# feat: add formula-derivation skill for research formula development

Source: [wanshuiyin/Auto-claude-code-research-in-sleep#48](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/pull/48)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/formula-derivation/SKILL.md`

## What to add / change

## Summary

Add `formula-derivation`, a community skill for pre-proof theory work.

It is useful when the theorem is not fixed yet and the user first needs to:
- choose the right object
- organize assumptions and notation
- build a coherent derivation line

## When to chain with `proof-writer`

Use them back-to-back when:
1. the theory object or assumptions are still unclear
2. the derivation needs to be structured first
3. the final claim will only be proved after that

Recommended workflow:
- `formula-derivation` -> fix object / assumptions / derivation skeleton
- `proof-writer` -> prove the final theorem / lemma / proposition

## Compatibility

The current output is designed to hand off cleanly to `proof-writer`:
- normalized object
- explicit assumptions
- notation
- local claim / target statement
- boundaries and non-claims

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
