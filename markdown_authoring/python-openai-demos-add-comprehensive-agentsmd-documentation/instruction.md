# Add comprehensive AGENTS.md documentation for coding agent onboarding

Source: [Azure-Samples/python-openai-demos#4](https://github.com/Azure-Samples/python-openai-demos/pull/4)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Overview

This PR adds a comprehensive `AGENTS.md` file to help coding agents work more efficiently with this repository. The documentation significantly reduces the time needed for agents to understand the codebase, set up their environment, and make changes correctly.

## What's Included

The `AGENTS.md` file provides:

### 1. **Repository Overview**
Clear description of the repository's purpose: a collection of Python scripts demonstrating OpenAI API usage with multiple LLM providers (GitHub Models, Azure OpenAI, OpenAI.com, and Ollama).

### 2. **Code Layout & Architecture**
Complete inventory of important files with descriptions:
- **25 Python example scripts** organized by category (chat completions, function calling, structured outputs, RAG)
- **Infrastructure files** (Bicep templates, azd scripts for Azure provisioning)
- **Configuration files** (pyproject.toml, requirements files, pre-commit config)
- **CI/CD workflows** (linting/formatting checks, GitHub Models integration tests)
- **Dev container configurations** (4 variants for different LLM providers)

### 3. **Environment Setup Instructions**
Agent-facing guidance for:
- Creating Python virtual environments
- Installing dependencies (requirements.txt, requirements-rag.txt, requirements-dev.txt)
- **Detecting available LLM providers** by checking environment variables:
  - **GitHub Models** (RECOMMENDED): Check for `GITHUB_TOKEN` environment variable
  - **Azure OpenAI**: Check for `AZURE_OPENAI_ENDPOINT` and 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
