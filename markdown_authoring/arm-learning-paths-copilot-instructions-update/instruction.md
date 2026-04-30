# Copilot instructions update

Source: [ArmDeveloperEcosystem/arm-learning-paths#2670](https://github.com/ArmDeveloperEcosystem/arm-learning-paths/pull/2670)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

This PR refines the Copilot instructions file to clarify content-level guidance for Learning Paths and install guides.

The changes focus on:
	•	Strengthening accessibility guidance (especially descriptive alt text for images)
	•	Making section recaps and progress markers explicit for Learning Paths
	•	Improving consistency in tone, wording, and product name emphasis
	•	Reducing AI-generated writing patterns in instructional content

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
