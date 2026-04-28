# Add CLAUDE & AGENTS md

Source: [fission/fission#3349](https://github.com/fission/fission/pull/3349)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

<!--  Thanks for sending a pull request! We request you provide detailed description as much as possible. -->

## Description
<!--- Describe your changes in detail. -->
<!-- Typically try to give details of what, why and how of the PR changes. -->

## Which issue(s) this PR fixes:
<!--
*Automatically closes linked issue when PR is merged.
Usage: `Fixes #<issue number>`, or `Fixes (paste link of issue)`.
-->
Fixes #

## Testing
<!--- Please describe in detail how you tested your changes. -->

## Checklist:
<!-- Please tick following checkboxes as per your understanding. -->
- [ ] I ran tests as well as code linting locally to verify my changes. 
- [ ] I have done manual verification of my changes, changes working as expected.
- [ ] I have added new tests to cover my changes.
- [ ] My changes follow contributing guidelines of Fission.
- [ ] I have signed all of my commits.

<!-- Reviewable:start -->
- - -
This change is [<img src="https://reviewable.io/review_button.svg" height="34" align="absmiddle" alt="Reviewable"/>](https://reviewable.io/reviews/fission/fission/3349)
<!-- Reviewable:end -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
