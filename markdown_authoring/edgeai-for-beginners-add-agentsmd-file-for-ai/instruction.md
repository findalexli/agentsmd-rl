# Add AGENTS.md file for AI coding agent guidance

Source: [microsoft/edgeai-for-beginners#110](https://github.com/microsoft/edgeai-for-beginners/pull/110)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Overview

This PR adds a comprehensive `AGENTS.md` file to the repository root, following the [agents.md](https://agents.md/) open format specification. This file provides AI coding agents with the context and instructions they need to effectively work on this educational repository.

## What is AGENTS.md?

`AGENTS.md` is a standardized "README for agents" that complements `README.md` by containing detailed technical instructions and context specifically designed for AI coding tools. It works across 20+ different AI coding agents including Cursor, Aider, GitHub Copilot, and many others.

## Key Sections Included

The `AGENTS.md` file provides comprehensive guidance across the following areas:

### Project Context
- **Project Overview**: Description of the educational repository, key technologies (Python, JavaScript/Electron, AI/ML frameworks), and architecture
- **Repository Structure**: Clear visual tree of the codebase layout including all 8 modules and 10 sample applications

### Development Instructions
- **Setup Commands**: Step-by-step instructions for Python virtual environments, Node.js dependencies, and Foundry Local setup
- **Development Workflow**: Guidance for both content development (Markdown) and sample application development (Python/JavaScript)
- **Testing Instructions**: Content validation procedures and sample application testing (unit, integration, E2E tests)

### Contribution Guidelines
- **Code Style Guidelines**: Conventions for Markdown content, Pyt

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
