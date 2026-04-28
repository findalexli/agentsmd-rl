# feat(skills): add prompt-scanner skill definition

Source: [alibaba/anolisa#256](https://github.com/alibaba/anolisa/pull/256)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `src/agent-sec-core/skills/prompt-scanner/SKILL.md`

## What to add / change

## Description

    Add SKILL.md for the prompt-scanner skill, which provides
    multi-layer prompt injection and jailbreak detection using:

    - L1 rule engine for fast regex-based matching
    - L2 ML classifier (Llama Prompt Guard 2) for semantic analysis

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

closes #

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
- [x] `sec-core` (agent-sec-core)
- [ ] `skill` (os-skills)
- [ ] `sight` (agentsight)
- [ ] Multiple / Project-wide

## Checklist

<!-- Check all that apply. -->

- [ ] I have read the [Contributing Guide](../CONTRIBUTING.md)
- [ ] My code follows the project's code style
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] I hav

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
