# Add `AGENTS.md`

Source: [NVIDIA/nvalchemi-toolkit-ops#31](https://github.com/NVIDIA/nvalchemi-toolkit-ops/pull/31)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

<!-- markdownlint-disable MD013-->
# ALCHEMI Toolkit-Ops Pull Request

## Description

This PR adds the `AGENTS.md` file, which should be automatically included in agents' contexts for common tools like Cursor, Claude, OpenCode, etc.

For the most part, it provides a very compact description for agents (and for humans too) of how to function within the codebase. In particular, it also provides strong guidance that agents are not allowed to commit code directly, and all code should be reviewed by humans first before committing.

## Type of Change

<!-- Mark the relevant option with an "x" -->

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Performance improvement
- [x] Documentation update
- [ ] Refactoring (no functional changes)
- [ ] CI/CD or infrastructure change

## Related Issues

N/A

## Changes Made

<!-- List the key changes made in this PR -->

- Initialize `AGENTS.md`

## Testing

<!-- Describe the tests you ran to verify your changes -->

- [ ] Unit tests pass locally (`make pytest`)
- [ ] Linting passes (`make lint`)
- [ ] New tests added for new functionality meets coverage expectations?

## Checklist

- [x] I have read and understand the [Contributing Guidelines](../CONTRIBUTING.md)
- [ ] I have updated the [CHANGELOG.md](../CHANGELOG.md)
- 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
