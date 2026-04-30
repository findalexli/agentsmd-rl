# 🔧 Delete CLAUDE.md

Source: [dubzzz/fast-check#6887](https://github.com/dubzzz/fast-check/pull/6887)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Description

<!-- Describe your change and explain what this PR is trying to solve -->

Fixes #issue-number

<!-- Add any additional context here -->

## Checklist

— _Don't delete this checklist and make sure you do the following before opening the PR_

- [ ] I have a full understanding of every line in this PR — whether the code was hand-written, AI-generated, copied from external sources or produced by any other tool
- [ ] I flagged the impact of my change (minor / patch / major) either by running `pnpm run bump` or by following the instructions from the changeset bot
- [ ] I kept this PR focused on a single concern and did not bundle unrelated changes
- [ ] I followed the [gitmoji](https://gitmoji.dev/) specification for the name of the PR, including the package scope (e.g. `🐛(vitest) Something...`) when the change targets a package other than `fast-check`
- [ ] I added relevant tests and they would have failed without my PR (when applicable)

<!-- PRs not checking all the boxes may take longer before being reviewed -->
<!-- More about contributing at https://github.com/dubzzz/fast-check/blob/main/CONTRIBUTING.md -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
