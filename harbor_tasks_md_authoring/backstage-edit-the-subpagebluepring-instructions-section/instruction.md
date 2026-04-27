# Edit the SubPageBluepring instructions section

Source: [backstage/backstage#33723](https://github.com/backstage/backstage/pull/33723)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `docs/.well-known/skills/plugin-full-frontend-system-migration/SKILL.md`

## What to add / change

## Hey, I just made a Pull Request!

Another small gotcha I found while testing this out, I think this would be a better approach.

Again I am no AI Agent skill expert but I think this would be preferable 😓 

#### :heavy_check_mark: Checklist

<!--- Please include the following in your Pull Request when applicable: -->

- [ ] A changeset describing the change and affected packages. ([more info](https://github.com/backstage/backstage/blob/master/CONTRIBUTING.md#creating-changesets))
- [x] Added or updated documentation
- [ ] Tests for new functionality and regression tests for bug fixes
- [ ] Screenshots attached (for UI changes)
- [x] All your commits have a `Signed-off-by` line in the message. ([more info](https://github.com/backstage/backstage/blob/master/CONTRIBUTING.md#developer-certificate-of-origin))

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
