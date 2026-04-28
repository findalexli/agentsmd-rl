# Add Copilot instructions for repository

Source: [1c-syntax/bsl-language-server#3562](https://github.com/1c-syntax/bsl-language-server/pull/3562)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Configures GitHub Copilot coding agent with repository-specific context per [best practices](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions).

## Changes

- **`.github/copilot-instructions.md`**: Comprehensive guidance covering:
  - Technology stack (Java 17, Gradle/Kotlin DSL, Spring Boot, ANTLR)
  - Build/test commands and development workflow
  - Diagnostic development process with links to existing docs
  - Code style conventions and bilingual documentation requirements
  - Project structure and CI/CD overview
  - Security considerations and common development tasks

Enables AI coding agents to understand project conventions, build processes, and development patterns without requiring manual context in each interaction.

<!-- START COPILOT CODING AGENT SUFFIX -->



<details>

<summary>Original prompt</summary>

> 
> ----
> 
> *This section details on the original issue you should resolve*
> 
> <issue_title>✨ Set up Copilot instructions</issue_title>
> <issue_description>Configure instructions for this repository as documented in [Best practices for Copilot coding agent in your repository](https://gh.io/copilot-coding-agent-tips).
> 
> <Onboard this repo></issue_description>
> 
> ## Comments on the Issue (you are @copilot in this section)
> 
> <comments>
> </comments>
> 


</details>

- Fixes 1c-syntax/bsl-language-server#3561

<!-- START COPILOT CODING AGENT TIPS -->
---

💬 We'd love your input! Share your thoughts on

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
