# fix(ce-pr-description): cap description size and add pre-apply preview

Source: [EveryInc/compound-engineering-plugin#605](https://github.com/EveryInc/compound-engineering-plugin/pull/605)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/ce-commit-push-pr/SKILL.md`
- `plugins/compound-engineering/skills/ce-commit/SKILL.md`
- `plugins/compound-engineering/skills/ce-pr-description/SKILL.md`

## What to add / change

## Summary

Large PRs were producing 145-200 line descriptions with 14+ H3 subsections that re-listed Summary content in more words — reviewers either burned through them or skipped past. This caps the Large tier at ~100-150 lines, adds a compression pass that removes the common inflation patterns, and inserts a preview-and-confirm step before `ce-commit-push-pr` overwrites an existing PR body.

## What changed

- **Step 5 sizing** — Large tier now targets ~100 lines / caps at 150 and says to use a Summary-level table when a PR has 10+ mechanisms, instead of spawning an H3 per mechanism.
- **New Step 8b compression pass** — cut Summary-duplicating sections, enumerated Commits lists, process-oriented Review sections, and any body running >30% over the sizing target.
- **Value-lead check on the Summary opening** — rewrite mechanism-first leads ("This PR introduces...") into outcome-first ones ("X previously failed; now...").
- **New writing principles** — no Commits section (GitHub shows commits in its own tab), no Review/process section (process doesn't help the reviewer evaluate code).
- **ce-commit-push-pr Step 6** — 100-word cap on free-text steering passed to `ce-pr-description`, with guidance that steering is for framing, not an exhaustive scope dump.
- **ce-commit-push-pr Step 7 (existing-PR rewrite)** — new preview step shows the new title, the first two Summary sentences, and total line count before `gh pr edit` is called. User can decline and pass steering back for a 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
