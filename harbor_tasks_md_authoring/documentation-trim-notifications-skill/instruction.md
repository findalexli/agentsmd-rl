# Trim Notifications SKILL

Source: [QuantConnect/Documentation#2331](https://github.com/QuantConnect/Documentation/pull/2331)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `03 Writing Algorithms/40 Live Trading/40 Notifications/SKILL.md`

## What to add / change

## Summary

Follow-up to #2330 (Add Notifications SKILL). Cuts the file from 132 to 107 lines without losing facts:

- Drop the **Common mistakes to avoid** section. Every entry duplicated content already in the two critical sections, the per-channel gotchas, or the checklist.
- Drop the **Cost model** column from the channels table. The single line in the Hourly free quota section ("overage costs 1 QCC; SMS always per-message at 1/10 QCC") covers the same ground without four near-identical cells.
- Tighten the cloud-only critical section into one sentence.
- Tighten the helper-wrapper paragraph.

No C# is added — the language-selection skill handles syntax mapping for skills that show Python.

## Test plan

- [x] `python validate-and-install-skills.py -v` reports `Validated 7 SKILL.md file(s), all OK.`
- [x] All facts from the dropped sections are still present elsewhere in the skill.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
