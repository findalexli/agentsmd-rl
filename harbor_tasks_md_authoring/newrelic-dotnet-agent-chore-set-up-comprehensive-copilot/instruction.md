# chore: ✨ Set up comprehensive Copilot instructions

Source: [newrelic/newrelic-dotnet-agent#3283](https://github.com/newrelic/newrelic-dotnet-agent/pull/3283)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

## Overview

Enhanced the `.github/copilot-instructions.md` file with comprehensive guidelines following <a href="https://gh.io/copilot-coding-agent-tips">GitHub's best practices for Copilot coding agent</a>.

## What Changed

The original file contained 9 bullet points with basic coding guidelines. This PR transforms it into a comprehensive, well-structured guide that provides context and actionable instructions for GitHub Copilot when working with this codebase.

## New Structure

The enhanced instructions now include:

### 📋 Repository Overview
- High-level description of the New Relic .NET Agent
- Key solutions (FullAgent.sln, Profiler.sln, IntegrationTests.sln, ContainerIntegrationTests.sln, UnboundedIntegrationTests.sln, BuildTools.sln)
- Important directory structure guide

### 💻 Coding Standards
- **C# Style Guidelines**: PascalCase, camelCase, and naming conventions aligned with `.editorconfig`
- **File Headers**: Standard license header format with example and clarification about copyright year
- **Backwards Compatibility**: Critical requirements for .NET Framework 4.6.2+ and .NET Standard 2.0+ support
- **Comments**: Guidelines for preserving documentation and explaining complex code

### 🧪 Testing
- **Unit Tests**: NUnit framework usage, modern assertions, JustMock Lite constraints
- **Integration Tests**: When to add them and reference to setup documentation
- **Running Tests**: Quick guide for Visual Studio Test Explorer

### 🔨 Building
- Visual Studio 2022 prer

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
