# Add AGENTS.md file with comprehensive agent instructions

Source: [microsoft/mcp-for-beginners#426](https://github.com/microsoft/mcp-for-beginners/pull/426)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Overview

This PR adds an `AGENTS.md` file to the repository root, following the [agents.md](https://agents.md/) open format. This file serves as a "README for agents" - providing AI coding agents with the context and instructions they need to work effectively on the MCP for Beginners curriculum.

## What is AGENTS.md?

`AGENTS.md` is a standardized Markdown file that complements human-focused documentation by containing detailed technical context specifically designed for AI coding agents. It works across 20+ different AI coding tools including Cursor, Aider, GitHub Copilot, and many others.

## Contents

The newly created `AGENTS.md` file includes:

### 📋 Project Overview
- Comprehensive description of the MCP for Beginners educational curriculum
- Key technologies: C#, Java, JavaScript, TypeScript, Python, Rust
- Frameworks: MCP SDK, Spring Boot, FastMCP, LangChain4j
- Architecture: 11 sequential modules (00-11) with hands-on labs

### 🛠️ Setup Commands
- Repository cloning and setup instructions
- Language-specific setup for TypeScript/JavaScript, Python, and Java projects
- Guidance for working with sample projects in different directories

### 📝 Development Workflow
- Documentation structure and organization
- How to make changes to the curriculum content
- Automated translation system workflow (48+ languages)
- Guidelines for working with translations and images

### ✅ Testing Instructions
- Documentation validation techniques
- Link checking and markdown linting
- 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
