# Add next-step suggestions to every ooo skill output

Source: [Q00/ouroboros#68](https://github.com/Q00/ouroboros/pull/68)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/evaluate/SKILL.md`
- `skills/evolve/SKILL.md`
- `skills/interview/SKILL.md`
- `skills/ralph/SKILL.md`
- `skills/run/SKILL.md`
- `skills/seed/SKILL.md`
- `skills/status/SKILL.md`
- `skills/unstuck/SKILL.md`

## What to add / change

## Summary

Right now when you finish an `ooo` step, you're left wondering "...okay, what now?" This adds a `📍 Next:` suggestion to every skill so users always know which command to run next.

- **interview** → suggests `ooo seed`
- **seed** → suggests `ooo run`
- **run** → suggests `ooo evaluate` (or retry on failure)
- **evaluate** → says "Done!" on pass, or points to `ooo ralph`/`ooo evolve` on rejection
- **evolve** → suggests `ooo evaluate` on convergence, `ooo unstuck` on stagnation
- **ralph** → suggests `ooo evaluate` on completion, `ooo unstuck` if maxed out
- **unstuck** → routes back to `ooo run` or `ooo ralph`
- **status** → suggests next action based on drift level

All changes are documentation-only (SKILL.md files). No code or runtime behavior affected.

Closes #58

## Test plan

- [x] Verified `📍` marker appears in both instructions and example output for all 8 skills
- [x] Confirmed workflow mapping is consistent — no skill suggests a command that doesn't exist
- [x] No existing content removed, only additions

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
