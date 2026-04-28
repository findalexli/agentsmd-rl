# Update/copilot instructions

Source: [IvanMurzak/Unity-MCP#460](https://github.com/IvanMurzak/Unity-MCP/pull/460)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

This pull request replaces the detailed project instructions in `.github/copilot-instructions.md` with a concise set of project guidelines. The new document focuses on code style, architecture, build/test procedures, conventions, integration points, and security, while removing the previous step-by-step instructions and troubleshooting sections.

Key changes:

**Documentation and Guidelines:**
* Replaced the detailed setup, build, and testing instructions with a high-level "Project Guidelines" document summarizing code style, project architecture, build/test commands, conventions, integration points, and security considerations.

**Removed Content:**
* Removed explicit instructions for environment setup, building, running, and testing both the Unity-MCP-Server and Unity-MCP-Plugin, as well as troubleshooting, CI/CD details, and manual validation steps.

**Code Style and Architecture:**
* Added clear code style conventions for C# and PowerShell, and outlined the structure and main components of the project (Plugin, Server, Installer, Unity-Tests).

**Build and Test Procedures:**
* Provided concise references to build and test commands/scripts, replacing the previous detailed command-by-command instructions.

**Project Conventions and Integration:**
* Summarized conventions for MCP tool implementation, documentation locations, versioning, communication protocols, and dependency management. ([.github/copilot-instructions.mdL1-R43](diffhunk://#diff-227c2c26cb2ee0

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
