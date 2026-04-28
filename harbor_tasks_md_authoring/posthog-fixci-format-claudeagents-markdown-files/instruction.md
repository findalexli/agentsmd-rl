# fix(ci): format .claude/agents markdown files with oxfmt

Source: [PostHog/posthog#48897](https://github.com/PostHog/posthog/pull/48897)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/agents/ingestion/pipeline-composition-doctor.md`
- `.claude/agents/ingestion/pipeline-step-doctor.md`

## What to add / change

## Summary

- Auto-format `.claude/agents/ingestion/pipeline-composition-doctor.md` and `.claude/agents/ingestion/pipeline-step-doctor.md` with oxfmt to fix the `Check markdown formatting with oxfmt` CI step that has been failing on master since PR #48666.
- Changes are purely whitespace: 4-space → 2-space indentation in code blocks and arrow function parenthesization — no content changes.

## Context

The `Frontend formatting` job (`Check markdown formatting with oxfmt` step) has been failing on master, which also blocks the `Frontend Tests Pass` gate. These two files were introduced in #48666 without being formatted with oxfmt first.


---

> [!NOTE]
> Created by [Mendral](https://mendral.com). Tag @mendral-app with feedback or questions.
>
> - [View implementation session](https://app.mendral.com/sessions/action:01KJ7RMA02X657DFAEWRMA2TC5)
> - Addresses [this insight](https://app.mendral.com/insights/01KJ7RM9YX8VEF6KHPGD14TF0Z)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
