# Fix typo in guidance section of SKILL.md

Source: [NeoLabHQ/context-engineering-kit#28](https://github.com/NeoLabHQ/context-engineering-kit/pull/28)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/ddd/skills/software-architecture/SKILL.md`

## What to add / change

The word "guidence" should be "guidance". Shouldn't it?

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> Fixes a spelling error in the software architecture skill documentation.
> 
> - Corrects typo in the introduction of `plugins/ddd/skills/software-architecture/SKILL.md` ("guidence" → "guidance")
> 
> <sup>Written by [Cursor Bugbot](https://cursor.com/dashboard?tab=bugbot) for commit 9dc42a79492f8c37674bb9d2b479577d95dc8321. This will update automatically on new commits. Configure [here](https://cursor.com/dashboard?tab=bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
