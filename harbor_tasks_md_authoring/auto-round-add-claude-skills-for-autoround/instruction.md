# Add Claude skills for AutoRound

Source: [intel/auto-round#1686](https://github.com/intel/auto-round/pull/1686)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/adapt-new-diffusion-model/SKILL.md`
- `.claude/skills/adapt-new-llm/SKILL.md`
- `.claude/skills/add-export-format/SKILL.md`
- `.claude/skills/add-inference-backend/SKILL.md`
- `.claude/skills/add-quantization-datatype/SKILL.md`
- `.claude/skills/add-vlm-model/SKILL.md`
- `.claude/skills/readme.md`
- `.claude/skills/review-pr/SKILL.md`

## What to add / change

## Description

Add Claude skills for AutoRound

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring
- [x] Other (please specify):

## Related Issues

<!-- Link to related issues using #issue_number -->

Fixes or relates to #

## Checklist Before Submitting

- [ ] My code has been tested locally.
- [ ] Documentation has been updated as needed.
- [ ] New or updated tests are included where applicable.

<!-- Optional: Tag reviewers or add extra notes below -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
