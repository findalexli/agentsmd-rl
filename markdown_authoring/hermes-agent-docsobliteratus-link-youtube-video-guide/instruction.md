# docs(obliteratus): link YouTube video guide in SKILL.md

Source: [NousResearch/hermes-agent#15808](https://github.com/NousResearch/hermes-agent/pull/15808)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/mlops/inference/obliteratus/SKILL.md`

## What to add / change

## Summary
Adds a 'Video Guide' section to the obliteratus built-in skill pointing at the walkthrough of a Hermes agent abliterating Gemma with OBLITERATUS, so the agent can surface it when a user wants a visual overview before running the workflow.

## Changes
- skills/mlops/inference/obliteratus/SKILL.md: new 'Video Guide' section with https://www.youtube.com/watch?v=8fG9BrNTeHs

## Validation
Markdown-only change. No code paths affected.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
