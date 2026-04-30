# [ai] CLAUDE.md: Document Zulip's quality philosophy and standards.

Source: [zulip/zulip#38892](https://github.com/zulip/zulip/pull/38892)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/CLAUDE.md`

## What to add / change

The aim is to make Claude less cavalier about things being busted only in edge cases or by not very much.

---
## Claude's commit message

Expand the Philosophy section to convey Zulip's engineering culture: the "move quickly without breaking things" strategy, systematic investment in quality, and the principle that no detail is too small to get right. Add specific guidance on visual precision, UI states, responsiveness, internationalization, and interaction paths.

Strengthen the Manual Testing checklist to be explicitly blocking rather than advisory, with more specific verification steps.

Add a "Treating Known Issues as Acceptable" pitfall to address the failure mode of discovering bugs during verification and noting them rather than fixing them.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
