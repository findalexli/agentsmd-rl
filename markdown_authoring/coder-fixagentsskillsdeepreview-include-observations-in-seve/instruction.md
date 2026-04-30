# fix(.agents/skills/deep-review): include observations in severity evaluation

Source: [coder/coder#23505](https://github.com/coder/coder/pull/23505)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/deep-review/SKILL.md`

## What to add / change

Observations bypassed the severity test entirely. A reviewer filing a convention violation as Obs meant it skipped both the upgrade check ("could this be worse than stated?") and the unnecessary-novelty gate (which only fired when *no* reviewer flagged the issue). The combination let issues pass through as dropped observations when they warranted P3+.

Two changes:
- Severity test now applies to findings **and** observations.
- Unnecessary novelty check now covers reviewer-flagged Obs.

Ported from the same fix in the personal deep-review skill, where the bug was discovered during a live review (a misplaced package filed as Obs bypassed all severity gates).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
