# add .agents/skills/build/SKILL.md for build conventions

Source: [tile-ai/tilelang#2019](https://github.com/tile-ai/tilelang/pull/2019)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/build/SKILL.md`

## What to add / change

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Documentation**
  * Added comprehensive build, installation, and testing guidance covering standard and alternative install methods, development-focused setup with direct build integration, optional incremental rebuild optimizations, a CMake-based workflow for rapid iteration, a warning about editable installs, common build feature flags (GPU/backends, build type), and example test commands including macOS Apple Silicon (Metal) test guidance.
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
