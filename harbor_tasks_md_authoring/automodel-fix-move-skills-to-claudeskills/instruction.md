# fix: move skills to .claude/skills

Source: [NVIDIA-NeMo/Automodel#1662](https://github.com/NVIDIA-NeMo/Automodel/pull/1662)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/developer-guide/SKILL.md`
- `.claude/skills/distributed-training/SKILL.md`
- `.claude/skills/launcher-config/SKILL.md`
- `.claude/skills/model-onboarding/SKILL.md`
- `.claude/skills/model-onboarding/llm-patterns.md`
- `.claude/skills/model-onboarding/moe-patterns.md`
- `.claude/skills/model-onboarding/vlm-patterns.md`
- `.claude/skills/parity-testing/SKILL.md`
- `.claude/skills/parity-testing/pitfalls.md`
- `.claude/skills/recipe-development/SKILL.md`

## What to add / change

# What does this PR do ?

Add a one line overview of what this PR aims to accomplish.

# Changelog

- Add specific line by line info of high level changes in this PR.

# Before your PR is "Ready for review"

**Pre checks**:

- [ ] Make sure you read and followed [Contributor guidelines](https://github.com/NVIDIA-NeMo/Automodel/blob/main/CONTRIBUTING.md)
- [ ] Did you write any new necessary tests?
- [ ] Did you add or update any necessary documentation?

If you haven't finished some of the above items you can still open "Draft" PR.

# Additional Information

- Related to # (issue)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
