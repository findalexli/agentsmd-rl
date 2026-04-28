# Add AGENTS.md file to repository root

Source: [microsoft/PhiCookBook#394](https://github.com/microsoft/PhiCookBook/pull/394)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary

This PR adds an `AGENTS.md` file to the repository root, providing AI coding agents with comprehensive context and instructions for working effectively with the PhiCookBook repository.

## What is AGENTS.md?

AGENTS.md is an open format designed to serve as a "README for agents" - a standardized, predictable location where AI coding tools can find detailed technical context, setup instructions, and development guidelines. It complements the existing README.md by providing agent-specific information without cluttering the human-focused documentation.

## What's Included

The AGENTS.md file provides comprehensive coverage of:

### Project Context
- Overview of PhiCookBook as a hands-on cookbook for Microsoft Phi models
- Key technologies: Python, C#/.NET, JavaScript across ONNX Runtime, PyTorch, Transformers, MLX, OpenVINO
- Repository structure explanation (`/code/`, `/md/`, `/translations/`)

### Development Setup
- GitHub Codespaces and Dev Containers instructions (pre-configured with Python 3.12 and Ollama)
- Local setup for Python, .NET, and JavaScript examples
- Platform-specific prerequisites and installation steps

### Working with the Repository
- How to run Jupyter notebooks, Python scripts, .NET projects, and JavaScript examples
- File format explanations (.ipynb, .py, .csproj, .js)
- Repository organization and navigation guide

### Development Guidelines
- Code style conventions from CONTRIBUTING.md
- Documentation standards (URL formatting, relative li

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
