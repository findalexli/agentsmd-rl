#  feat(skill): add clawhub-skill-mng skill for agent to support clawhub market

Source: [alibaba/anolisa#315](https://github.com/alibaba/anolisa/pull/315)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `src/os-skills/others/clawhub-skill-mng/SKILL.md`

## What to add / change

## Description

<!-- Provide a clear and concise description of the changes. Include motivation and context. -->
add clawhub-skill-mng skill for agent to support clawhub market
## Related Issue

<!--
  REQUIRED: Every PR must be linked to an existing issue.
  Use one of the closing keywords so the issue closes automatically on merge:

    closes #<number>
    fixes #<number>
    resolves #<number>

  If this is a trivial typo / doc-only fix with no issue, write:
    no-issue: <reason>
-->

closes #314

## Type of Change

<!-- Check all that apply. -->

- [ ] Bug fix (non-breaking change that fixes an issue)
- [x] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Refactoring (no functional change)
- [ ] Performance improvement
- [ ] CI/CD or build changes

## Scope

<!-- Which sub-project does this PR affect? -->

- [ ] `cosh` (copilot-shell)
- [ ] `sec-core` (agent-sec-core)
- [x] `skill` (os-skills)
- [ ] `sight` (agentsight)
- [ ] Multiple / Project-wide

## Checklist

<!-- Check all that apply. -->

- [x] I have read the [Contributing Guide](../CONTRIBUTING.md)
- [x] My code follows the project's code style
- [x] I have added tests that prove my fix is effective or that my feature works
- [ ] I have updated the documentation accordingly
- [ ] For `cosh`: Lint passes, type check pass

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
