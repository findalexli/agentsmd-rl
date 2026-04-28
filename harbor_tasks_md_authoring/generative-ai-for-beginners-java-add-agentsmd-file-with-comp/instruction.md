# Add AGENTS.md file with comprehensive project documentation for AI coding agents

Source: [microsoft/Generative-AI-for-beginners-java#65](https://github.com/microsoft/Generative-AI-for-beginners-java/pull/65)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary

This PR adds an `AGENTS.md` file to the repository root, providing comprehensive documentation specifically designed for AI coding agents working on this project.

## What is AGENTS.md?

`AGENTS.md` is an open format that serves as a "README for agents" - a dedicated, predictable place to provide context and instructions to help AI coding agents work effectively on a project. It follows the public guidance at https://agents.md/ and is compatible with 20+ AI coding tools including Cursor, Aider, GitHub Copilot, and others.

## What's Included

The `AGENTS.md` file provides agent-focused documentation covering:

### Project Overview
- Description of the educational Generative AI for Java repository
- Key technologies: Java 21, Spring Boot 3.5.x, Spring AI 1.1.x, Maven, LangChain4j
- Architecture overview of the multi-chapter course structure

### Setup Commands
- Three environment setup options (GitHub Codespaces, Local Dev Container, Local Setup)
- Prerequisites and dependency installation
- Configuration for GitHub Models and Azure OpenAI

### Development Workflow
- Complete project structure overview
- Exact commands for running Spring Boot applications
- Instructions for building and testing each sample project
- Hot reload setup for development

### Testing Instructions
- Maven test commands with various options
- Test structure and file locations
- Manual testing guidelines for interactive applications
- GitHub Models testing limitations

### Code Style Guidel

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
