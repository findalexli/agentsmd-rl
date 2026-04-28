# ✨ Add GitHub Copilot instructions for the repository

Source: [spacetx/starfish#2093](https://github.com/spacetx/starfish/pull/2093)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

This PR sets up GitHub Copilot instructions for the starfish repository by creating a comprehensive `.github/copilot-instructions.md` file, following the best practices documented at https://gh.io/copilot-coding-agent-tips.

## What's Included

The Copilot instructions file provides AI coding assistants with essential context about the project:

### Project Context
- **Overview**: Description of starfish as a Python library for image-based spatial transcriptomics
- **Technology Stack**: Python 3.9+, pytest, mypy, flake8, Sphinx
- **Key Dependencies**: numpy, scikit-image, xarray, h5py, matplotlib, and others (without version constraints to avoid maintenance burden)

### Development Standards
- **Code Style**: Type annotation requirements (PEP 484/526), numpydoc documentation style
- **Linting**: flake8 configuration with project-specific ignores
- **Testing**: pytest markers (`slow`, `napari`), parallel execution, coverage requirements

### Project Architecture
- **Pipeline Components**: How to create new algorithms by subclassing base components
- **Core Workflow**: Image filtering → feature identification → decoding → segmentation
- **Directory Structure**: Organization of core code, examples, notebooks, and documentation

### Practical Guidelines
- **Build Commands**: `make fast`, `make test`, `make docs-html`, etc.
- **Development Setup**: `make install-dev` for proper environment configuration
- **Adding Features**: Step-by-step guide for implementing new algorithms
- **

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
