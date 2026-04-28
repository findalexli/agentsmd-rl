# doc: add AGENTS.md

Source: [shovel-heroes-org/shovel-heroes#63](https://github.com/shovel-heroes-org/shovel-heroes/pull/63)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

This pull request adds a new documentation file, `AGENTS.md`, which defines the role settings and development guidelines for AI Agents in the project. The document provides a comprehensive overview of the project's architecture, coding standards, workflow, and best practices for both frontend and backend development, with a strong emphasis on minimal changes, type safety, and security.

Key additions in this documentation:

**Project Overview and Architecture:**
* Introduces the Shovel-Heroes platform, outlining its purpose and technical stack, including frontend, backend, and type system choices.
* Details the project directory structure to help developers navigate the codebase efficiently.

**Agent Role and Development Principles:**
* Clearly defines the expected expertise for AI Agents, covering backend (Fastify, PostgreSQL), frontend (React, Vite, Tailwind), and TypeScript type safety.
* Establishes the "minimal change principle," advocating for targeted, non-intrusive code modifications and discouraging unnecessary refactoring or deviation from established patterns.

**Coding Standards and Workflow:**
* Specifies adherence to the project's ESLint configuration, code style guidelines for both backend and frontend, and OpenAPI-driven type safety practices.
* Outlines manual verification steps, security requirements, and a step-by-step workflow for adding features, fixing bugs

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
