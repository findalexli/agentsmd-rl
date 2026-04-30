# Add AGENTS.md file with comprehensive agent documentation

Source: [microsoft/ai-agents-for-beginners#359](https://github.com/microsoft/ai-agents-for-beginners/pull/359)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Overview

This PR adds an `AGENTS.md` file to the repository root, following the open format specified at https://agents.md/. This file serves as a "README for agents" - providing AI coding agents with the context and instructions they need to work effectively on this project.

## What is AGENTS.md?

`AGENTS.md` is a standardized Markdown file that provides detailed technical context and instructions for automated coding tools and AI agents. It complements the human-focused `README.md` by containing agent-specific guidance that helps AI systems understand the project structure, setup requirements, development workflows, and contribution guidelines.

## What's Included

The new `AGENTS.md` file provides comprehensive documentation across the following areas:

### Project Overview
- Description of the "AI Agents for Beginners" educational course
- Key technologies: Python 3.12+, Jupyter Notebooks, Semantic Kernel, AutoGen, Microsoft Agent Framework, Azure AI Services
- Architecture overview of the lesson-based structure with multi-language support

### Setup Commands
- Complete prerequisites and initial setup steps
- Virtual environment creation and dependency installation
- Environment variable configuration for both GitHub Models (free tier) and Azure AI services

### Development Workflow
- Instructions for running Jupyter notebooks across different frameworks
- Framework-specific guidance (Semantic Kernel, AutoGen, Microsoft Agent Framework, Azure AI Agent Service)
- Note

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
