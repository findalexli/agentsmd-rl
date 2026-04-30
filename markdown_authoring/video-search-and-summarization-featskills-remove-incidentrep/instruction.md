# feat(skills): remove incident-report skill

Source: [NVIDIA-AI-Blueprints/video-search-and-summarization#144](https://github.com/NVIDIA-AI-Blueprints/video-search-and-summarization/pull/144)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/incident-report/SKILL.md`

## What to add / change

## Description

Removes the `incident-report` skill from `skills/`.

## Checklist
- [x] I am familiar with the [Contributing Guidelines](https://github.com/NVIDIA-AI-Blueprints/video-search-and-summarization/blob/HEAD/CONTRIBUTING.md).
- [x] New or existing tests cover these changes.
- [x] The documentation is up to date with these changes.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
