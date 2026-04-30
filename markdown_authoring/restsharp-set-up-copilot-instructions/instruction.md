# Set up Copilot instructions

Source: [restsharp/RestSharp#2325](https://github.com/restsharp/RestSharp/pull/2325)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

### **User description**
## Description

Resolves #2323

Adds `.github/copilot-instructions.md` to configure GitHub Copilot coding agent per [best practices](https://gh.io/copilot-coding-agent-tips).

Contents:
- Project overview and repository structure
- Build/test commands (`dotnet build`, `dotnet test`, `dotnet pack`)
- Multi-targeting guidance (netstandard2.0 through net10.0, conditional compilation)
- Code style: C# preview, nullable settings, license header template
- Testing: xUnit + FluentAssertions + AutoFixture, WireMock for HTTP
- Source generators: `[GenerateImmutable]`, `[GenerateClone]`, `[Exclude]`
- Central package management via `Directory.Packages.props`
- PR checklist

## Purpose
This pull request is a:

- [ ] Bugfix (non-breaking change which fixes an issue)
- [x] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)


## Checklist

- [ ] I have added tests that prove my fix is effective or that my feature works
- [x] I have added necessary documentation (if appropriate)

<!-- START COPILOT CODING AGENT SUFFIX -->



<details>

<summary>Original prompt</summary>

> 
> ----
> 
> *This section details on the original issue you should resolve*
> 
> <issue_title>✨ Set up Copilot instructions</issue_title>
> <issue_description>Configure instructions for this repository as documented in [Best practices for Copilot coding agent in your repository](https://

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
