# Add GitHub Copilot instructions for PR template and Fantomas formatting

Source: [CompositionalIT/farmer#1228](https://github.com/CompositionalIT/farmer/pull/1228)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

## Plan: Add GitHub Copilot instructions for PR template and Fantomas formatting

- [x] Explore repository structure and understand requirements
- [x] Create `.github/copilot-instructions.md` with instructions about:
  - Following the PR template format
  - Running Fantomas to format F# code before committing
  - Adhering to coding standards from CONTRIBUTING.md
  - Including documentation, tests, and release notes
- [x] Update instructions to match PR template exactly (multiple refinements)
- [x] Verify the file is in the correct location for GitHub Copilot to read
- [x] Code review and address feedback
- [x] Add clarification about release notes based on maintainer feedback

## Summary

Created a comprehensive `.github/copilot-instructions.md` file that provides GitHub Copilot with all the necessary instructions for contributing to the Farmer repository. This file includes:

1. **PR Template Requirements**: Instructions to follow the PR template with exact wording matching the template, including:
   - Issue linking format
   - Changes listing
   - Contributing guidelines statement
   - Complete checklist with exact wording
   - Minimal example configuration section
   
2. **Fantomas Formatting**: Clear, step-by-step instructions on how to run Fantomas to format F# code, with emphasis that this is required and enforced by CI

3. **Coding Standards**: The specific F# coding standards from CONTRIBUTING.md:
   - Never use `yield`
   - Prefer specific list comprehension syntax


## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
