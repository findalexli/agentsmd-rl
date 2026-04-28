# agent: add CLAUDE.md and claude skills

Source: [flashinfer-ai/flashinfer#2240](https://github.com/flashinfer-ai/flashinfer/pull/2240)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/add-cuda-kernel/skill.md`
- `.claude/skills/benchmark-kernel/skill.md`
- `.claude/skills/debug-cuda-crash/skill.md`
- `CLAUDE.md`

## What to add / change

<!-- .github/pull_request_template.md -->

## 📌 Description

Add CLAUDE.md as contribution guide to agents (and human).
Add several skills (adding an CUDA operator to flashinfer, debug, profiling), this list will grow in the future.

## 🔍 Related Issues

<!-- Link any related issues here -->

## 🚀 Pull Request Checklist

Thank you for contributing to FlashInfer! Before we review your pull request, please make sure the following items are complete.

### ✅ Pre-commit Checks

- [x] I have installed `pre-commit` by running `pip install pre-commit` (or used your preferred method).
- [x] I have installed the hooks with `pre-commit install`.
- [x] I have run the hooks manually with `pre-commit run --all-files` and fixed any reported issues.

> If you are unsure about how to set up `pre-commit`, see [the pre-commit documentation](https://pre-commit.com/).

## 🧪 Tests

- [x] Tests have been added or updated as needed.
- [x] All tests are passing (`unittest`, etc.).

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
Co-Authored-By: aleozlx <aleyang@nvidia.com>
Co-Authored-By: bkryu <bkryu@nvidia.com>
Co-Authored-By: nvmbreughe <nvmbreughe@nvidia.com>
Co-Authored-By: jimmyzho <jimmzhou@nvidia.com>
Co-Authored-By: cyx-6 <yaxingc@nvidia.com>

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **New Features**
  * Element-wise tensor scaling (in-place/out-of-place) with JIT-backed modules and a simp

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
