# Add comprehensive GitHub Copilot instructions for ProxiFyre development

Source: [wiresock/proxifyre#90](https://github.com/wiresock/proxifyre/pull/90)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

This PR adds a comprehensive `.github/copilot-instructions.md` file that provides GitHub Copilot coding agents with detailed instructions for working effectively in the ProxiFyre codebase.

## Key Features

**Platform-Specific Guidance**: The instructions clearly document that ProxiFyre is a Windows-only application requiring specific dependencies (Windows Packet Filter, Visual Studio Runtime, vcpkg) and provide explicit warnings about build limitations on Linux/macOS environments.

**Precise Build Instructions**: Includes exact commands for:
- vcpkg setup and package installation (`ms-gsl`, `boost-pool`)
- NuGet package restoration
- MSBuild commands with proper parameters for different platforms (x86, x64, ARM64)

**Critical Timing Information**: Documents expected build times with proper timeout recommendations:
- vcpkg package installation: 10-15 minutes (30+ minute timeout recommended)
- Solution builds: 5-8 minutes (15+ minute timeout recommended)
- Includes "NEVER CANCEL" warnings for long-running operations

**Manual Validation Scenarios**: Provides specific steps for testing functionality:
- SOCKS5 proxy configuration and testing
- Log file monitoring in `/logs` directory
- Network traffic validation
- Windows Service installation testing

**Repository Navigation**: All documented commands have been validated to work correctly, including file structure navigation, project discovery, and source code analysis.

## Example Usage

The instructions enable agents to quickl

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
