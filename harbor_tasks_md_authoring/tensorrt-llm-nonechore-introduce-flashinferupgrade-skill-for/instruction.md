# [None][chore] Introduce flashinfer-upgrade skill for automated version bumps

Source: [NVIDIA/TensorRT-LLM#12987](https://github.com/NVIDIA/TensorRT-LLM/pull/12987)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/flashinfer-upgrade/SKILL.md`

## What to add / change

## Summary
- Add `flashinfer-upgrade` skill to `.claude/skills/` that automates upgrading the `flashinfer-python` dependency
- Fetches releases from GitHub, lets user choose stable vs nightly, updates all 4 pinned version files, verifies compatibility, and creates a PR
- Includes prerequisite checks for `USE_GH_TOKEN` and `NVIDIA_GH_TOKEN` with setup instructions

## Test plan
- [x] Invoke `/flashinfer-upgrade` and verify the interactive workflow runs correctly
- [x] Verify skill appears in the registered skills list


<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Documentation**
  * Added internal workflow documentation for managing dependency updates.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
