# Add repository Copilot PR review instructions

Source: [openvinotoolkit/openvino#34188](https://github.com/openvinotoolkit/openvino/pull/34188)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

## Details
- add .github/copilot-instructions.md for OpenVINO
- define reviewer priorities: correctness, security, performance, API/binding consistency, and test impact
- codify component-aware checks aligned with CODEOWNERS/labeler/CI workflows
- define severity levels and actionable review comment format

## Motivation
Improve automated PR review quality and consistency for OpenVINO with repository-specific guidance.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
