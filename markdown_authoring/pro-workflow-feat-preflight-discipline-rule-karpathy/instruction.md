# feat: pre-flight discipline rule (karpathy principles)

Source: [rohitg00/pro-workflow#46](https://github.com/rohitg00/pro-workflow/pull/46)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `rules/pre-flight-discipline.mdc`
- `skills/pro-workflow/SKILL.md`

## What to add / change

## Summary

Adds a fifth always-on rule that encodes the four upstream-failure preventions [Andrej Karpathy named](https://x.com/karpathy/status/2015883857489522876) for LLM coding: silent assumptions, overcomplicated diffs, drive-by edits, vague success criteria.

Pro-workflow already quotes Karpathy's 80/20 line in `SKILL.md` but none of the four behavioral principles were encoded as rules. The closest existing rules — `quality-gates` and `self-correction` — both fire *after* the mistake. This one fires before.

| Rule | Prevents |
|------|----------|
| Surface, don't assume | Wrong interpretation, hidden confusion, missing tradeoffs |
| Minimum viable code | 200-line diffs that should be 50, speculative abstractions |
| Stay in your lane | Drive-by refactors, "improvements" to adjacent code |
| Verifiable goals | Endless re-clarification, "make it work" loops |

## Changes

- **New:** `rules/pre-flight-discipline.mdc` (`alwaysApply: true`, ~60 lines)
- **Edit:** `skills/pro-workflow/SKILL.md` — adds §1b "Pre-Flight Discipline" between Self-Correction (§1) and Worktrees (§2), with a CLAUDE.md snippet and a pointer to the rule file
- **No changes** to existing rules, agents, hooks, commands, or contexts

## Attribution

Adapted from [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) (MIT) — single-skill repo of the same four principles. Reframed lightly to match pro-workflow's voice (`pre-flight-discipline` vs. `karpathy-guidelines`

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
