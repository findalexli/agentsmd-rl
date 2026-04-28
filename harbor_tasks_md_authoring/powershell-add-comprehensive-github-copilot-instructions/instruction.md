# ✨ Add comprehensive GitHub Copilot instructions

Source: [pnp/powershell#5122](https://github.com/pnp/powershell/pull/5122)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

## Overview

This PR adds comprehensive GitHub Copilot instructions to the repository by creating `.github/copilot-instructions.md`, as requested in the issue. This file provides context-specific guidance to help GitHub Copilot generate more accurate and relevant code suggestions when working with the PnP PowerShell codebase.

## What's Included

The Copilot instructions file provides detailed guidance across multiple areas:

### 📋 Project Context
- Complete overview of PnP PowerShell (750+ cmdlets for Microsoft 365 environments)
- Tech stack details: .NET 8, C# 12, PowerShell 7.4+
- Key characteristics: cross-platform support, community-driven, active development

### 🗂️ Repository Structure
- Comprehensive directory layout with explanations
- Location of cmdlets, build scripts, and documentation
- Feature area organization (Admin, Apps, Lists, Sites, Graph, etc.)

### 💻 Development Patterns
- Standard cmdlet class structure with complete code examples
- Naming conventions following PowerShell best practices (Verb-PnPNoun)
- Base class usage guide (PnPWebRetrievalsCmdlet, PnPGraphCmdlet, PnPAdminCmdlet)
- Required attributes documentation for permissions and output types
- PipeBind patterns for flexible parameter input
- **Backward compatibility guidance**: Always add `[Alias()]` attribute when renaming cmdlets to maintain backward compatibility

### 📐 Coding Standards
- C# style guide specific to this repository (tabs for indentation)
- Naming conventions (PascalCase, camel

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
