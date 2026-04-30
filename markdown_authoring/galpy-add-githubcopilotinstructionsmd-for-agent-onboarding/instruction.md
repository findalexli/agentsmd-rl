# Add .github/copilot-instructions.md for agent onboarding

Source: [jobovy/galpy#780](https://github.com/jobovy/galpy/pull/780)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

## Repository Onboarding: Creating .github/copilot-instructions.md

### Completed Tasks

- [x] Explore repository structure and documentation
- [x] Review README, CONTRIBUTING, and other documentation files
- [x] Examine GitHub Actions workflows (build.yml, build_windows.yml)
- [x] Review build configuration (setup.py, pyproject.toml)
- [x] Check pre-commit hooks and linting configuration
- [x] Install dependencies and build the package (with and without GSL)
- [x] Run basic tests to understand test structure
- [x] Document repository size and structure
- [x] Create comprehensive .github/copilot-instructions.md file (282 lines, ~1,328 words)
- [x] Validate the instructions file with test commands
- [x] Run code review (no issues found)
- [x] Run security checks (no code changes to analyze)
- [x] Validate markdown syntax
- [x] Address PR feedback from @jobovy:
  - Added context about when Torus code installation is needed
  - Removed unnecessary test configuration section
  - Corrected test dependencies (numba tests, added astropy)
  - Added orbit tests to potential workflow
  - Added PR #760 as example
  - Removed [ci skip] mentions
  - Added `-k` test selection tip

### Summary

Successfully created and refined a comprehensive `.github/copilot-instructions.md` file (now 275 lines) based on maintainer feedback.

<!-- START COPILOT CODING AGENT SUFFIX -->



<details>

<summary>Original prompt</summary>

Your task is to "onboard" this repository to Copilot coding agent by addi

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
