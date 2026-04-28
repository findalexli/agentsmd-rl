# feat(skills): updating all skills with igniteui-cli mcp refs

Source: [IgniteUI/igniteui-angular#17236](https://github.com/IgniteUI/igniteui-angular/pull/17236)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/igniteui-angular-components/SKILL.md`
- `skills/igniteui-angular-components/references/charts.md`
- `skills/igniteui-angular-components/references/data-display.md`
- `skills/igniteui-angular-components/references/directives.md`
- `skills/igniteui-angular-components/references/feedback.md`
- `skills/igniteui-angular-components/references/form-controls.md`
- `skills/igniteui-angular-components/references/layout-manager.md`
- `skills/igniteui-angular-components/references/layout.md`
- `skills/igniteui-angular-components/references/mcp-setup.md`

## What to add / change

Closes #  

## Description
<!-- Provide a brief summary of the changes introduced in this PR. -->


## Motivation / Context
<!-- Why is this change needed? Link to the related issue(s) or discussion. -->


### Type of Change (check all that apply):
 - [ ] Bug fix
 - [ ] New functionality
 - [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
 - [ ] Refactoring (no functional changes)
 - [ ] Documentation
 - [ ] Demos
 - [ ] CI/CD
 - [ ] Tests
 - [ ] Changelog
 - [x] Skills/Agents

### Component(s) / Area(s) Affected:
<!-- List the component(s) or area(s) this PR touches, e.g. Grid, Combo, Theming -->


## How Has This Been Tested?
<!-- Describe the tests you ran to verify your changes. Include relevant details so reviewers can reproduce. -->
 - [ ] Unit tests
 - [ ] Manual testing
 - [ ] Automated e2e tests

### Test Configuration:
 - **Angular version**: 
 - **Browser(s)**: 
 - **OS**: 

## Screenshots / Recordings
<!-- If applicable, add screenshots or recordings to help explain the visual changes. -->


## Checklist:
 - [ ] All relevant tags have been applied to this PR
 - [ ] This PR includes unit tests covering all the new code ([test guidelines](https://github.com/IgniteUI/igniteui-angular/wiki/Test-implementation-guidelines-for-Ignite-UI-for-Angular))
 - [ ] This PR includes API docs for newly added methods/properties ([api docs guidelines](https://github.com/IgniteUI/igniteui-angular/wiki/Documentation-Guidelines))
 - [

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
