# Expand AI-ism coverage: new words, dedup, let's pattern

Source: [conorbronsdon/avoid-ai-writing#2](https://github.com/conorbronsdon/avoid-ai-writing/pull/2)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`

## What to add / change

## Summary
- Add 15 common AI-ism words/phrases to the replace table: `nuanced`, `crucial`, `multifaceted`, `ecosystem`, `myriad`, `plethora`, `deep dive`/`dive into`, `unpack`, `bolster`, `spearhead`, `resonate`, `revolutionize`, `facilitate`, `underpin`
- Deduplicate filler phrases that appeared in both the word table and the filler section (`in order to`, `due to the fact that`, `at the end of the day`)
- Add "let's" constructions as a standalone category — broader than just "let's dive in" under chatbot artifacts

## Test plan
- [ ] Run the skill against text containing the new flagged words and verify they get caught
- [ ] Confirm existing detections still work as before

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
