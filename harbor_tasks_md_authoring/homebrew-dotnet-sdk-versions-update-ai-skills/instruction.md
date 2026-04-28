# Update AI skills

Source: [isen-ng/homebrew-dotnet-sdk-versions#506](https://github.com/isen-ng/homebrew-dotnet-sdk-versions/pull/506)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.aiskills/fix-ci/SKILL.md`
- `.aiskills/new-cask/SKILL.md`
- `.aiskills/update-cask/SKILL.md`

## What to add / change

See the PR for the intended changes to the listed file(s).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
