# feat: add consolidation support and overlap detection to `ce:compound` and `ce:compound-refresh` skills

Source: [EveryInc/compound-engineering-plugin#372](https://github.com/EveryInc/compound-engineering-plugin/pull/372)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/ce-compound-refresh/SKILL.md`
- `plugins/compound-engineering/skills/ce-compound/SKILL.md`

## What to add / change

## Summary

Both `ce:compound` and `ce:compound-refresh` now understand that `docs/solutions/` is a **document set**, not just a collection of independent files. This means they can detect when docs overlap, consolidate redundant ones, and avoid creating duplicates in the first place.

**ce:compound** now checks for overlap before creating a new doc. If an existing doc already covers the same problem, it updates that doc instead of creating a duplicate.

**ce:compound-refresh** gains two new maintenance actions — **Consolidate** (merge overlapping docs) and **Delete** (replacing the old Archive concept — git history is the archive). A new Document-Set Analysis phase evaluates docs against each other, not just against the codebase, catching redundancy that individual doc review misses. Also renames `mode:autonomous` to `mode:autofix` for consistency with other skills where we've introduced this.

**Net result:** In benchmarks against the old versions, the new skills prevented duplicate doc creation in 66% of the overlap scenarios, found a consolidation opportunity the old skill missed entirely, and showed no regressions on non-overlap cases.

## Optimization approach

Used `skill-creator` to measure improvement: 3 test scenarios per skill, run against both new (branch) and old (main) versions as parallel subagents. Each test graded against 4 behavioral assertions (24 total).

**ce:compound tests:** high-overlap doc (should update existing), no-overlap doc (regres

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
