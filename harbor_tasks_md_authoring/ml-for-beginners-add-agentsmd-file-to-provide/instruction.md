# Add AGENTS.md file to provide AI coding agents with project context

Source: [microsoft/ML-For-Beginners#879](https://github.com/microsoft/ML-For-Beginners/pull/879)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Overview

This PR adds a comprehensive `AGENTS.md` file to the repository root, following the [agents.md specification](https://agents.md/). This file serves as a "README for agents" - providing AI coding tools with the detailed technical context and instructions they need to work effectively on this project.

## What is AGENTS.md?

`AGENTS.md` is an open standard designed to help AI coding agents understand project structure, development workflows, and contribution guidelines. It complements the human-focused README.md by including agent-specific technical instructions and commands.

## Contents

The AGENTS.md file includes comprehensive information about:

### Project Structure
- Overview of the 12-week, 26-lesson ML curriculum
- Dual-language support (Python with Jupyter notebooks and R with R Markdown)
- Vue.js quiz application architecture
- Automated translation system via GitHub Actions
- Repository organization and typical lesson structure

### Development Workflows
- **Python/R Lessons**: Setup and execution of Jupyter notebooks and R Markdown files
- **Quiz Application**: npm commands for development, building, and linting
- **Documentation**: Docsify setup for local documentation serving
- **Translation System**: Automated workflow details and important warnings

### Setup and Commands
- Python dependencies installation (Jupyter, Scikit-learn, Pandas, NumPy)
- R package installation (tidyverse, tidymodels, caret)
- Quiz app setup and development server
- Documen

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
