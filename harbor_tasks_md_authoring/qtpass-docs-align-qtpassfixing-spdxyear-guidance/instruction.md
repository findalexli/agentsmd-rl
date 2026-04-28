# docs: align qtpass-fixing SPDX-year guidance with repo practice

Source: [IJHack/QtPass#1163](https://github.com/IJHack/QtPass/pull/1163)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.opencode/skills/qtpass-fixing/SKILL.md`

## What to add / change

<!-- kody-pr-summary:start -->
docs: Update SPDX copyright year guidance in `SKILL.md`

This pull request revises the documentation in `.opencode/skills/qtpass-fixing/SKILL.md` to provide updated guidance on specifying copyright years in SPDX headers.

The previous guidance recommended using `YYYY` as a placeholder. This change updates the documentation to instruct contributors to use the actual year the file was created, explicitly stating that placeholders or year ranges are not permitted. This aligns the documented practice with existing repository conventions and feedback from past code reviews.
<!-- kody-pr-summary:end -->

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Documentation**
  * Updated SPDX copyright-year convention guidelines to require single literal creation years instead of placeholders or year ranges in copyright text declarations.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
