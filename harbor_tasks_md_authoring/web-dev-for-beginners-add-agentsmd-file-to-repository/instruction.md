# Add AGENTS.md file to repository root

Source: [microsoft/Web-Dev-For-Beginners#1524](https://github.com/microsoft/Web-Dev-For-Beginners/pull/1524)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Overview

This PR adds a comprehensive `AGENTS.md` file to the repository root, providing AI coding agents with the context and instructions they need to work effectively on this educational web development curriculum.

## What is AGENTS.md?

`AGENTS.md` is an open format file that serves as a "README for agents" - a standardized, predictable location where AI coding tools can find detailed technical context about a project. It complements the human-focused `README.md` by containing agent-specific instructions and workflows.

## What's Included

The new `AGENTS.md` file provides comprehensive documentation across 11 major sections:

### 1. **Project Overview**
- Educational curriculum description and architecture
- Key components: 24 lessons, multiple projects, quiz system, translation infrastructure
- Technologies: HTML, CSS, JavaScript, Vue.js 3, Vite, Node.js, Express, Python

### 2. **Setup Commands**
Specific, executable commands for each project type:
- Quiz App (Vue 3 + Vite)
- Bank Project API (Node.js + Express)
- Browser Extension projects
- Space Game projects
- Python-based Chat Assistant

### 3. **Development Workflow**
- Guidelines for content contributors
- Learning path for students
- Live development server instructions

### 4. **Testing Instructions**
- Linting commands for each project
- Manual testing approaches
- Pre-submission verification steps

### 5. **Code Style Guidelines**
- JavaScript (ES6+, ESLint standards)
- HTML/CSS (semantic, responsive)
-

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
