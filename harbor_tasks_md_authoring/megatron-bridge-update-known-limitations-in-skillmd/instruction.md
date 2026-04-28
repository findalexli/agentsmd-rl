# Update known limitations in SKILL.md

Source: [NVIDIA-NeMo/Megatron-Bridge#3437](https://github.com/NVIDIA-NeMo/Megatron-Bridge/pull/3437)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/perf-techniques/memory-tuning/SKILL.md`

## What to add / change

There was a pytorch upstream update that fixes this limitation.  https://github.com/pytorch/pytorch/pull/169491

# What does this PR do ?

Add a one line overview of what this PR aims to accomplish.

# Changelog

- Add specific line by line info of high level changes in this PR.

# GitHub Actions CI

See the [CI section](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/main/CONTRIBUTING.md#-running-github-ci)in the Contributing doc for how to trigger the CI. A Nvidia developer will need to approve and trigger the CI for external contributors.

# Before your PR is "Ready for review"

**Pre checks**:

- [ ] Make sure you read and followed [Contributor guidelines](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/main/CONTRIBUTING.md)
- [ ] Did you write any new necessary tests?
- [ ] Did you add or update any necessary documentation?
- [ ] Does the PR affect components that are optional to install? (Ex: Numba, Pynini, Apex etc)
  - [ ] Reviewer: Does the PR have correct import guards for all optional libraries?

If you haven't finished some of the above items you can still open "Draft" PR.

# Additional Information

- Related to # (issue)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
