# ✨ Add Copilot instructions for React Native Windows samples repository

Source: [microsoft/react-native-windows-samples#1075](https://github.com/microsoft/react-native-windows-samples/pull/1075)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

This PR implements comprehensive Copilot instructions for the react-native-windows-samples repository to help GitHub Copilot better understand the codebase structure, development patterns, and best practices.

## What's Added

Created `.github/copilot-instructions.md` with detailed guidance covering:

- **Repository Overview**: Purpose and relationship to main React Native Windows/macOS repos
- **Technology Stack**: React Native Windows 0.79+, C++/WinRT, C#, TypeScript/JavaScript
- **Repository Structure**: Samples organization, legacy code, documentation, and CI/CD
- **Development Environment**: Prerequisites, setup instructions, and common commands
- **Sample Projects**: Detailed information about Calculator, NativeModuleSample, and ContinuousIntegration samples
- **Build System**: GitHub Actions workflows, build matrix (Debug/Release, x86/x64/ARM64)
- **Code Patterns**: File structure conventions, naming patterns, and coding standards
- **Testing Approach**: Jest configuration, native code testing, and integration testing
- **Common Tasks**: Adding samples, upgrading versions, working with native code
- **Troubleshooting**: Solutions for build failures, Metro issues, and native module problems
- **Best Practices**: Guidelines for contributors and cross-platform development

## Benefits

These instructions will help Copilot:
- Generate more accurate code suggestions for React Native Windows development
- Understand the multi-language nature of the repository (JS/TS, C++, C#

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
