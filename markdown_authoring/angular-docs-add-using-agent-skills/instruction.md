# docs: add "Using Agent Skills" + command to skills `README.md`

Source: [angular/angular#68156](https://github.com/angular/angular/pull/68156)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/dev-skills/README.md`

## What to add / change

## PR Checklist

Please check if your PR fulfills the following requirements:

- [x] The commit message follows our guidelines: https://github.com/angular/angular/blob/main/contributing-docs/commit-message-guidelines.md
- [ ] Tests for the changes have been added (for bug fixes / features)
- [ ] Docs have been added / updated (for bug fixes / features)

## PR Type

What kind of change does this PR introduce?

<!-- Please check the one that applies to this PR using "x". -->

- [ ] Bugfix
- [ ] Feature
- [ ] Code style update (formatting, local variables)
- [ ] Refactoring (no functional changes, no api changes)
- [ ] Build related changes
- [ ] CI related changes
- [x] Documentation content changes
- [ ] angular.dev application / infrastructure changes
- [ ] Other... Please describe:

## What is the current behavior?

I and others have noticed that the command to download skills was missing from the Skills readme. 

Issue Number: N/A

## What is the new behavior?

Copy/pasted the doc section on how to download the skills.

## Does this PR introduce a breaking change?

- [ ] Yes
- [x] No

<!-- If this PR contains a breaking change, please describe the impact and migration path for existing applications below. -->

## Other information

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
