# Add GitHub Copilot instructions

Source: [alefragnani/vscode-project-manager#852](https://github.com/alefragnani/vscode-project-manager/pull/852)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

## Setup Copilot Instructions

- [x] Analyze the repository structure and understand the codebase
- [x] Review the package.json and understand the VS Code extension structure
- [x] Create `.github/copilot-instructions.md` with comprehensive instructions
- [x] Validate the instructions file is properly formatted
- [x] Request code review
- [x] Run security checks (CodeQL)
- [x] Address feedback: Remove version numbers from Technology Stack and Key Dependencies sections
- [x] Address feedback: Remove redundant paragraph about license compliance (already covered in General Principles)

## Summary

Successfully created and refined comprehensive GitHub Copilot instructions at `.github/copilot-instructions.md` following best practices from https://gh.io/copilot-coding-agent-tips.

The instructions provide project overview, architecture, coding conventions, and development guidelines without hardcoded version numbers, making them easier to maintain as dependencies are updated.

<!-- START COPILOT ORIGINAL PROMPT -->



<details>

<summary>Original prompt</summary>

> 
> ----
> 
> *This section details on the original issue you should resolve*
> 
> <issue_title>✨ Set up Copilot instructions</issue_title>
> <issue_description>Configure instructions for this repository as documented in [Best practices for Copilot coding agent in your repository](https://gh.io/copilot-coding-agent-tips).
> 
> <Onboard this repo></issue_description>
> 
> ## Comments on the Issue (you are @copilot in this

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
