# Add AGENTS.md file for AI coding agent context

Source: [microsoft/Generative-AI-for-beginners-dotnet#408](https://github.com/microsoft/Generative-AI-for-beginners-dotnet/pull/408)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Overview

This PR adds a comprehensive `AGENTS.md` file to the repository root, following the [agents.md](https://agents.md/) open format specification. This file provides AI coding agents with the context and instructions they need to work effectively on this project.

## What is AGENTS.md?

`AGENTS.md` is an emerging standard format that serves as a "README for agents" - a dedicated, predictable place to provide context and instructions to help AI coding tools understand and contribute to a project. It complements `README.md` by containing detailed technical context that coding agents need but might clutter human-focused documentation.

## What's Included

The `AGENTS.md` file provides comprehensive guidance across the following areas:

### 📋 Project Overview & Architecture
- Clear description of the lesson-based repository structure
- Multi-language support details (8 translations)
- Key technologies and frameworks (.NET 9, Microsoft.Extensions.AI, Semantic Kernel, Azure OpenAI, Ollama, GitHub Models)

### ⚙️ Setup & Configuration
- Prerequisites and requirements
- Step-by-step setup for all three AI providers:
  - **GitHub Models** (recommended for beginners)
  - **Azure OpenAI** (enterprise/cloud)
  - **Ollama** (local models)
- Model pulling and configuration commands

### 🔨 Development Workflows
- GitHub Codespaces setup (recommended path)
- Local development procedures
- Running sample applications (SpaceAINet, HFMCP.GenImage, etc.)
- Hot reload and watch mode usag

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
