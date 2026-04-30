# Merge cursorrules into claude.md and update

Source: [Couchers-org/couchers#8324](https://github.com/Couchers-org/couchers/pull/8324)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursorrules`
- `CLAUDE.md`

## What to add / change

This was on the to-do for a bit. Now that both can pick up claude.md and most of us use claude I'm merging the `.cursorrules` into the `claude.md` and deleting the former.

Also added some missing stuff about the new date localization functions.

<!--
Include screenshots and any necessary dev environment adjustments such as editing .env files.
Fill applicable checklists below, or remove those that don't apply.
-->

## For maintainers
<!-- Untick the following if you'd prefer that maintainers don't push commits/merge your branch. -->
- [x] Maintainers can push commits to my branch
- [x] Maintainers can merge this PR for me

<!--
Remember to request review from couchers-org/web, couchers-org/backend or an individual.
Once your code is approved, you can merge it if you have write access.
--->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
