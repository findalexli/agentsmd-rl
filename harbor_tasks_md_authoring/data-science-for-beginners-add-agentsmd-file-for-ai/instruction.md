# Add AGENTS.md file for AI coding agent guidance

Source: [microsoft/Data-Science-For-Beginners#678](https://github.com/microsoft/Data-Science-For-Beginners/pull/678)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Overview

This PR adds a comprehensive `AGENTS.md` file to the repository root to provide AI coding agents with the context and instructions they need to work effectively on this Data Science for Beginners curriculum.

## What is AGENTS.md?

`AGENTS.md` follows the open format defined at https://agents.md/ - it serves as a "README for agents" that provides detailed technical context specifically for AI coding tools, complementing the human-focused README.md.

## What's Included

The new `AGENTS.md` file provides:

### Project Context
- Overview of the 10-week, 20-lesson data science curriculum structure
- Key technologies: Jupyter notebooks (Python), Vue.js quiz app, Docsify documentation
- Architecture explanation: lesson modules, translations, quiz system

### Actionable Setup Commands
- Python environment setup with common data science libraries (pandas, numpy, matplotlib)
- Quiz application setup and development (`npm install`, `npm run serve`)
- Docsify documentation server setup
- Visualization project setup for individual lessons

### Development Workflows
- Working with Jupyter notebooks and lesson structure
- Quiz application development with hot-reload
- Adding and managing translations
- Lesson content organization patterns

### Testing & Quality
- Quiz application testing procedures
- Notebook validation approaches
- Documentation testing with Docsify
- Linting commands for Vue.js projects

### Code Style Guidelines
- Python conventions for Jupyter notebooks (P

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
