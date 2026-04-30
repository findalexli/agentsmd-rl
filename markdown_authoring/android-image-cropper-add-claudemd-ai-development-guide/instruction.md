# Add CLAUDE.md - AI Development Guide

Source: [CanHub/Android-Image-Cropper#685](https://github.com/CanHub/Android-Image-Cropper/pull/685)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

# AI Development Guide for Android Image Cropper

This PR adds comprehensive documentation for AI-assisted development on the Android Image Cropper library.

## What's Included

### CLAUDE.md
Complete project guide covering:
- **Project Overview**: Tech stack, module structure, version info
- **Code Style & Conventions**: Kotlin style, indentation, organization  
- **Build & Test Commands**: All gradle commands needed
- **Development Workflow**: Branch naming, commit messages, testing strategy
- **API Change Guidelines**: Breaking changes, deprecation process
- **Release Process**: Snapshot and official release workflows
- **Common Tasks**: Adding features, fixing bugs, updating dependencies, translations
- **Important Files**: Key configuration and source files
- **Key Classes**: Main library components to understand
- **Security Considerations**: URI validation, permissions, input validation
- **Troubleshooting**: Build, test, and lint issue resolution
- **AI Assistant Guidelines**: Best practices for AI-assisted development

## Purpose

This document provides context and guidelines for AI assistants (like Claude Code) working on this project, ensuring:
- Consistent code quality and style
- Proper testing and documentation  
- Backward compatibility in public APIs
- Security-first development
- Understanding of project constraints (minSdk 21, published library serving thousands of apps)

## Related PRs

Subsequent PRs will add the .claude/ directory structure with specializ

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
