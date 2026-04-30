# Add AGENTS.md file with comprehensive agent instructions

Source: [microsoft/generative-ai-for-beginners#980](https://github.com/microsoft/generative-ai-for-beginners/pull/980)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary

This PR adds an `AGENTS.md` file to the repository root, following the standard format defined at https://agents.md/. This file serves as a "README for agents" - providing AI coding agents with the context and instructions they need to work effectively on this project.

## What is AGENTS.md?

`AGENTS.md` is an open format designed to give coding agents detailed technical context and instructions. It complements `README.md` by containing agent-specific guidance that might be too detailed for human-focused documentation.

## What's Included

The new `AGENTS.md` file provides comprehensive documentation covering:

### 📋 Project Overview
- Description of the 21-lesson Generative AI curriculum
- Key technologies: Python 3.9+, TypeScript/Node.js, Azure OpenAI, OpenAI API, GitHub Models
- Repository structure with 40+ language translations

### ⚙️ Setup Commands
- Repository cloning and initial setup
- Python virtual environment creation and dependency installation
- Node.js/TypeScript setup for individual lesson examples
- Dev Container configuration for GitHub Codespaces

### 🔧 Development Workflow
- Environment variable configuration using `.env` file
- Running Python examples with virtual environments
- Building and running TypeScript applications
- Working with Jupyter Notebooks
- Understanding "Learn" vs "Build" lesson types

### 📝 Code Style Guidelines
- Python conventions (PEP 8, pylint, dotenv patterns)
- TypeScript conventions (tsconfig, nodemon, build process)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
