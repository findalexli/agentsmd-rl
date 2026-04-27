# docs: clarify test generation responsibility in hive skill

Source: [aden-hive/hive#3901](https://github.com/aden-hive/hive/pull/3901)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/hive/SKILL.md`

## What to add / change

## Description

Clarifies that the hive workflow and hive-test tools provide orchestration,
guidelines, templates, and execution utilities, while test code is written by
the calling agent using the Write tool. This aligns the hive skill documentation
with current behavior.


## Type of Change

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [x] Documentation update
- [ ] Refactoring (no functional changes)

## Related Issues

N/A (documentation-only change)

## Changes Made

- Change 1 - Clarified test generation responsibility in `.claude/skills/hive/SKILL.md` to reflect delegation to the `hive-test` skill
- Change 2 - Removed implication in the hive workflow that hive-test tools directly write test code
- Change 3 - Aligned documentation language with existing implementation

## Testing

Describe the tests you ran to verify your changes:

- [ ] Unit tests pass (`cd core && pytest tests/`)
- [ ] Lint passes (`cd core && ruff check .`)
- [x] Manual testing performed

## Checklist

- [x] My code follows the project's style guidelines
- [x] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [x] I have made corresponding changes to the documentation
- [x] My changes generate no new warnings
- [ ] I h

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
