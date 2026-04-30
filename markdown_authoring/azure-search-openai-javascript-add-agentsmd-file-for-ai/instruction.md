# Add AGENTS.md file for AI coding agent guidance

Source: [Azure-Samples/azure-search-openai-javascript#241](https://github.com/Azure-Samples/azure-search-openai-javascript/pull/241)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Overview

This PR adds an `AGENTS.md` file to the repository root to provide comprehensive documentation for AI coding agents working on this project. The file follows the [agents.md](https://agents.md/) open format standard, which is designed to give coding agents the context and instructions they need to work effectively.

## What is AGENTS.md?

`AGENTS.md` serves as a "README for agents" - a standardized, predictable place to provide technical context and instructions that help AI coding tools understand and contribute to a project. It complements the human-focused `README.md` by containing detailed technical instructions specifically for automated tools.

## Contents

The `AGENTS.md` file includes comprehensive documentation across the following areas:

### Project Overview
- Description of the ChatGPT + Enterprise data RAG application architecture
- npm workspace structure with three main packages (webapp, search, indexer)
- Key technologies: TypeScript, React, Lit, Fastify, Vite, Azure services

### Setup & Development
- Prerequisites and installation commands
- First-time Azure deployment with `azd up`
- Local development workflow (requires Azure deployment first)
- Running services individually or concurrently
- Environment variable management with Azure Developer CLI

### Testing
- Unit tests with Node.js test runner and c8 coverage
- E2E tests with Playwright configuration
- Load tests with k6
- Test file locations and specific commands

### Code Style & Build
- 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
