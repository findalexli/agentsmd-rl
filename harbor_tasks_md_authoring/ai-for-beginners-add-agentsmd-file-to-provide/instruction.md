# Add AGENTS.md file to provide AI coding agents with comprehensive project context

Source: [microsoft/AI-For-Beginners#535](https://github.com/microsoft/AI-For-Beginners/pull/535)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Overview

This PR adds an `AGENTS.md` file to the repository root, following the [agents.md](https://agents.md/) standard format. This file serves as a "README for AI coding agents," providing detailed technical context and instructions that help AI coding tools work effectively on this project.

## What is AGENTS.md?

`AGENTS.md` is an open format designed to provide coding agents with the context and instructions they need to work effectively on a project. It complements `README.md` by containing detailed technical instructions for automated tools while keeping the human-focused documentation clean and accessible.

## What's Included

The new `AGENTS.md` file provides comprehensive documentation covering:

### Core Setup & Development
- **Project Overview**: Description of the 12-week, 24-lesson AI curriculum with key technologies (Python, Jupyter, TensorFlow, PyTorch, Vue.js)
- **Setup Commands**: Detailed instructions for conda environment setup, Jupyter notebooks, devcontainer usage, and Vue.js quiz app
- **Development Workflow**: Guidance for local development, VS Code integration, cloud options (GitHub Codespaces, Binder, Azure), and GPU-accelerated environments

### Testing & Code Quality
- **Testing Instructions**: Validation approaches specific to educational content (notebook execution, quiz app testing, translation validation)
- **Code Style**: Python and JavaScript conventions, file organization, and ESLint configuration
- **Build & Deployment**: Quiz app buil

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
