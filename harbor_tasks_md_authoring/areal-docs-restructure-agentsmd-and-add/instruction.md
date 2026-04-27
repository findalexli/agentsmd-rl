# docs: restructure AGENTS.md and add CLAUDE.md symlink

Source: [inclusionAI/AReaL#783](https://github.com/inclusionAI/AReaL/pull/783)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

## Description

Improve documentation structure, fix incorrect file paths, and enhance directory descriptions with Trainer example.


## Type of Change

<!-- Mark the relevant option with an 'x' -->

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not
  work as expected)
- [x] Documentation update
- [ ] Code refactoring (no functional changes)
- [ ] Performance improvement
- [ ] Test coverage improvement

## Checklist

<!-- Mark with 'x' what you've done -->

- [x] I have read the [Contributing Guide](../CONTRIBUTING.md)
- [ ] I have run formatting tools (pre-commit or manual)
- [ ] I have run relevant unit tests and they pass
- [ ] I have added tests for new functionality
- [x] I have updated documentation if needed
- [x] My branch is up to date with main
- [ ] This PR introduces breaking changes (if yes, fill out details below)
- [ ] If this PR changes documentation, I have built and previewed it locally with
  `jb build docs`
- [x] No critical issues raised by AI reviewers (`/gemini review`)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
