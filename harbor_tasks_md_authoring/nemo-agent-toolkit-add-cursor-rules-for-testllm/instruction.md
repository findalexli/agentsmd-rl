# Add cursor rules for `test_llm` from `nvidia-nat-test` package

Source: [NVIDIA/NeMo-Agent-Toolkit#774](https://github.com/NVIDIA/NeMo-Agent-Toolkit/pull/774)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/nat-test-llm.mdc`

## What to add / change

## Description
<!-- Note: The pull request title will be included in the CHANGELOG. -->
<!-- Provide a standalone description of changes in this PR. -->
<!-- Reference any issues closed by this PR with "closes #1234". All PRs should have an issue they close-->
Close

- Added: `.cursor/rules/nat-test-llm.mdc` with usage rules for `nat_test_llm` (YAML example, fields response_seq/delay_ms, builder pattern, wrapper hints).  ￼

I separated this code from the original big PR because I want to make sure I don't mess things up for cursor rules :)

## By Submitting this PR I confirm:
- I am familiar with the [Contributing Guidelines](https://github.com/NVIDIA/NeMo-Agent-Toolkit/blob/develop/docs/source/resources/contributing.md).
- We require that all contributors "sign-off" on their commits. This certifies that the contribution is your original work, or you have rights to submit it under the same license, or a compatible license.
  - Any contribution which contains commits that are not Signed-Off will not be accepted.
- When the PR is ready for review, new or existing tests cover these changes.
- When the PR is ready for review, the documentation is up to date with these changes.


<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **New Features**
  * Introduced a deterministic Test LLM for workflows/tests with configurable cyclic response sequences and optional per-call latency; compatible with common wrapper type

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
