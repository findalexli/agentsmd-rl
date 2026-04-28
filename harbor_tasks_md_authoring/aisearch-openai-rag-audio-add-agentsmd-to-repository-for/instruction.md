# Add AGENTS.md to repository for coding agent onboarding

Source: [Azure-Samples/aisearch-openai-rag-audio#126](https://github.com/Azure-Samples/aisearch-openai-rag-audio/pull/126)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Overview

This PR adds a comprehensive `AGENTS.md` file to the repository root to onboard coding agents (like GitHub Copilot's automation agents) and help them work efficiently and correctly in this codebase.

## What is AGENTS.md?

`AGENTS.md` is a machine-readable instruction file that provides automated coding agents with explicit guidance on:
- Repository structure and key files
- Environment setup and dependency management
- Development workflows and testing procedures
- Linting rules and code conventions
- Common pitfalls and gotchas
- Pre-PR validation checklists

## Why is this important?

Providing high-quality, explicit repository instructions dramatically reduces:
- ❌ Broken or failing CI/build attempts
- ❌ Wasted exploration (excessive grep/find searches)
- ❌ Incorrect environment setup
- ❌ PR churn due to missing context

## What's included in this AGENTS.md?

The file contains all required sections as specified in the canonical guidance:

1. **Overview** - Project description (VoiceRAG with Azure OpenAI GPT-4o Realtime API and Azure AI Search), main technologies (Python 3.11+, aiohttp, React/TypeScript, Vite, Bicep), and primary entry points

2. **Code layout** - Comprehensive directory structure covering:
   - Backend Python code (`app/backend/`)
   - Frontend React application (`app/frontend/`)
   - Infrastructure templates (`infra/`)
   - Helper scripts (`scripts/`)
   - Documentation and workflows

3. **Running the code** - Step-by-step instructions for:


## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
