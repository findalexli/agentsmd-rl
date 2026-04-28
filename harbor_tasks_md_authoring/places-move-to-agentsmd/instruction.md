# Move to AGENTS.md

Source: [custom-components/places#395](https://github.com/custom-components/places/pull/395)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`
- `AGENTS.md`

## What to add / change

This pull request consolidates and streamlines the repository's autonomous agent instructions by removing the previous `.github/copilot-instructions.md` file and introducing a new, clearer `AGENTS.md` at the root. The new document provides more concise, organized, and repo-specific guidelines for agents, clarifying expectations for coding standards, testing, permissions, and local tooling.

Key changes include:

**Documentation consolidation and clarity:**
* Removed `.github/copilot-instructions.md` and replaced it with a new `AGENTS.md` at the root, providing a single, authoritative source for agent instructions. [[1]](diffhunk://#diff-227c2c26cb2ee0ce0f46a320fc48fbcbdf21801a57f59161b1d0861e8aad55f5L1-L74) [[2]](diffhunk://#diff-a54ff182c7e8acf56acfd6e4b9c3ff41e2c41a31c9b211b2deb9df75d9a478f9R1-R94)
* The new `AGENTS.md` is more concise, better organized by theme, and tailored to actual repository practices, reducing duplication and ambiguity.

**Updated and clarified agent guidelines:**
* Refined coding standards and testing expectations, including requirements for typing, docstrings (now requiring NumPy format), modularity, and code coverage, with clearer instructions for test structure and when to update documentation.
* Provided explicit instructions for agent permissions, venv usage, local tooling commands, and when agents may perform network or install operations.

**Home Assistant integration and repo-specific practices:**
* Added explicit instructions fo

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
