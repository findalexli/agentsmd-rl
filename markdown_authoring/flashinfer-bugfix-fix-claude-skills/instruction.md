# bugfix: fix claude skills

Source: [flashinfer-ai/flashinfer#2275](https://github.com/flashinfer-ai/flashinfer/pull/2275)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/add-cuda-kernel/SKILL.md`
- `.claude/skills/benchmark-kernel/SKILL.md`
- `.claude/skills/debug-cuda-crash/SKILL.md`

## What to add / change

<!-- .github/pull_request_template.md -->

## 📌 Description

Skills defined in #2240 doesn't make effect because of missing metadata and wrong file name.
This PR fixes the issue.

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

## Reviewer Notes

<!-- Optional: anything you'd like reviewers to focus on, concerns, etc. -->


<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **New Features**
  * Scale kernel now available as a public API for end-users
  * New benchmarking guide and tools for kernel performance measurement

* **Documentation**
  * Updated tutorial documentation with structured metadata
  * Added comprehensive benchmarking guidance with examples

* **Tests**
  * Implemented unit tests to validate kernel

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
