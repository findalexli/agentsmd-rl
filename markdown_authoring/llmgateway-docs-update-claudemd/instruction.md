# docs: update CLAUDE.md

Source: [theopenco/llmgateway#713](https://github.com/theopenco/llmgateway/pull/713)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* Documentation
  * Updated documentation to explain how to authenticate curl requests against the local API using a test token for local development.
  * Provides an example command and guidance on required headers to streamline local testing.
  * No changes to application behavior or configuration; documentation-only improvement.
  * Helps reduce setup friction and confusion for developers and testers when verifying endpoints locally.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
