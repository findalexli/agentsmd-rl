# Create .cursorrules for NNStreamer PR guidelines

Source: [nnstreamer/nnstreamer#4824](https://github.com/nnstreamer/nnstreamer/pull/4824)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursorrules`

## What to add / change

Added cursor rules for NNStreamer PR reviews to ensure maintainable and CI-friendly code changes.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
