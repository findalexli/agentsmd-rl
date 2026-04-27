# feat(skills): add user feedback and attachment analysis to fix-sentry

Source: [iOfficeAI/AionUi#2491](https://github.com/iOfficeAI/AionUi/pull/2491)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/fix-sentry/SKILL.md`
- `.claude/skills/fix-sentry/references/report-template.md`
- `.claude/skills/fix-sentry/references/triage-rules.md`

## What to add / change

## Summary

- Add **Step 1.5b: Attachment Analysis** to fix-sentry skill for processing user feedback issues (`event.type: default`) and issues without stack traces
- Add **Feedback fix** triage category (Step C2) in triage-rules with decision table for log/screenshot analysis
- Add `include_feedback` config parameter (default `false`) to opt-in to feedback issue processing
- Update report templates with feedback fix sections and summary line

Closes #2489

## Test plan

- [x] Verified end-to-end with ELECTRON-SS (Sentry user feedback): fetched event → listed attachments → downloaded screenshot + logs.gz → diagnosed dark mode UI issue → located code → applied fix
- [x] Existing skill behavior unchanged when `include_feedback=false` (default)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
