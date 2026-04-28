# Add global copilot-instructions.md

Source: [microsoft/winget-pkgs#361169](https://github.com/microsoft/winget-pkgs/pull/361169)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

## Summary

Adds a .github/copilot-instructions.md file to provide Copilot with foundational context about the repository. This complements the existing scoped instruction files in .github/instructions/.

### What's included
- Repository overview (manifest-only repo, not a code project)
- Critical performance rule (never scan the full \manifests/\ directory)
- Manifest structure and naming conventions
- PR conventions (one package per PR, validation pipeline, auto-merge)
- Validation and testing commands (\winget validate\, \SandboxTest.ps1\)
- Tooling reference (YamlCreate, winget-create)
- CI/CD overview (PSScriptAnalyzer, spell check, Azure DevOps pipelines)
- Code style (YAML formatting, PascalCase fields, editorconfig)
 ###### Microsoft Reviewers: [Open in CodeFlow](https://microsoft.github.io/open-pr/?codeflow=https://github.com/microsoft/winget-pkgs/pull/361169)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
