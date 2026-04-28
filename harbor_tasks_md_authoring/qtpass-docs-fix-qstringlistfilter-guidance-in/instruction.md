# docs: fix QStringList::filter() guidance in qtpass-fixing skill

Source: [IJHack/QtPass#1165](https://github.com/IJHack/QtPass/pull/1165)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.opencode/skills/qtpass-fixing/SKILL.md`

## What to add / change

<!-- kody-pr-summary:start -->
Refined the guidance in the `qtpass-fixing` skill documentation regarding the use of `QStringList::filter()` for removing environment variables.

The update clarifies that `QStringList::filter()` is unsuitable for prefix-based removal because it selects matching entries (rather than removing them) and matches substrings anywhere in the string, which can lead to unintended over-matching. The documentation now explicitly advises using `std::remove_if` with `startsWith` for prefix-based environment variable removal, providing a more accurate explanation of the "bad" example's behavior and the "good" example's intent.
<!-- kody-pr-summary:end -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
