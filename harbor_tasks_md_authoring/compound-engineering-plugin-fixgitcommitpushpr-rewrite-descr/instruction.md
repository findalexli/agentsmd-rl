# fix(git-commit-push-pr): rewrite descriptions as net result, not changelog

Source: [EveryInc/compound-engineering-plugin#558](https://github.com/EveryInc/compound-engineering-plugin/pull/558)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md`

## What to add / change

## Summary

PR description updates produced changelog-style additions ("here's what changed since last time") instead of rewriting to reflect the PR's net result. Now all description writes and rewrites describe what the PR does when merged, treating every update as a fresh description of the current state.

## Changes

**Net-result framing (the behavioral fix):**
- Step 7 existing-PR flow: replaced "updated to reflect the new changes" with explicit "rewrite from scratch" directive
- DU-3 description update workflow: same rewrite-from-scratch language, clarified the "compare and confirm" step is for the user's benefit, not a signal the description should narrate differences
- "Describe the net result" writing principle: extended to explicitly cover description updates

**Succinctness pass (~70 lines net reduction):**
- Cross-platform question tool boilerplate (repeated 7 times) defined once at the top, all instances replaced with "ask the user"
- Removed examples that restated their directives: narrative frame example, numbering/references code blocks, markdown table format example, 3 of 6 model slug examples
- Converted evidence "not possible" criteria from dense prose to bullet list
- Compressed decision tree entries, sizing intro, and several writing principles that were over-explained

---

[![Compound Engineering](https://img.shields.io/badge/Built_with-Compound_Engineering-6366f1)](https://github.com/EveryInc/compound-engineering-plugin)
![Claude Code](https://img.shiel

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
