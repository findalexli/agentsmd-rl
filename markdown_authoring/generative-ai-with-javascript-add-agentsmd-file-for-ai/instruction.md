# Add AGENTS.md file for AI coding agent integration

Source: [microsoft/generative-ai-with-javascript#172](https://github.com/microsoft/generative-ai-with-javascript/pull/172)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Overview

This PR adds a comprehensive `AGENTS.md` file at the repository root following the [agents.md](https://agents.md/) open format specification. This file provides AI coding agents with the context and instructions they need to effectively work on this educational repository.

## What is AGENTS.md?

`AGENTS.md` is an emerging standard that serves as a "README for agents" - a dedicated, predictable place to provide context and instructions to help AI coding agents understand and contribute to a project. It complements the human-focused `README.md` by containing detailed technical instructions that coding agents need.

## What's Included

The `AGENTS.md` file provides comprehensive coverage of:

### Project Context
- **Educational Repository Structure**: Explains this is a multi-lesson learning course with 8 independent lesson packages
- **Key Technologies**: JavaScript/Node.js ES Modules, TypeScript, OpenAI SDK, Model Context Protocol (MCP), Express.js, and GitHub Models
- **Architecture Overview**: Details the lesson-based structure, main companion app, and documentation organization

### Actionable Instructions
- **Setup Commands**: Step-by-step instructions for both GitHub Codespaces (recommended) and local development
- **Development Workflow**: How to work with individual lessons, run TypeScript builds, and navigate the repository
- **Testing Approach**: Manual testing procedures appropriate for educational content, including MCP inspector usage
- **Code Style G

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
