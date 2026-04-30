# Add comprehensive GitHub Copilot instructions for UXsim repository

Source: [toruseo/UXsim#225](https://github.com/toruseo/UXsim/pull/225)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

- [x] Add comprehensive GitHub Copilot instructions for UXsim repository
- [x] Merge latest main branch to include pytest-xdist serialization fixes (#223)

## Key Features

**Complete Setup and Installation Guide:**
- Exact installation commands with validated timing expectations (2-4 minutes for main install)
- Python version requirements and dependency management
- Optional dependencies for advanced features (osmnx, pytorch, streamlit)

**Comprehensive Testing Framework:**
- Full test suite commands with proper timeout warnings
- Example tests: 12+ minutes total runtime with "NEVER CANCEL" warnings
- Verification tests: 30-120 seconds per file with specific timeout recommendations
- Parallel testing options using pytest-xdist

**Manual Validation Scenarios:**
- Simple linear network validation (1-2 seconds)
- Basic network with visualization (15-20 seconds)  
- Large-scale Chicago scenario with 1M+ vehicles (40-60 seconds)
- Interactive Python validation snippets

**Timing Expectations and Performance Guidelines:**
- Measured and documented exact timing for all major operations
- Explicit "NEVER CANCEL" warnings for long-running processes
- Build timeout recommendations with 50% safety buffers
- Performance expectations for different simulation scales

**Common Issues and Gotchas:**
- Optional dependency failures (osmnx, pytorch) with installation guidance
- GUI limitations in headless environments
- Test exclusions and their reasons
- Known working workarounds

## Recent U

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
