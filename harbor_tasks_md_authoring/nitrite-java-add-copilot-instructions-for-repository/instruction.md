# Add Copilot instructions for repository

Source: [nitrite/nitrite-java#1177](https://github.com/nitrite/nitrite-java/pull/1177)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Configure GitHub Copilot coding agent instructions as documented in best practices guide.

## Changes

- **Created `.github/copilot-instructions.md`** with repository-specific guidance:
  - Project overview and multi-module Maven structure (9 modules documented)
  - Build environment: Java 11 minimum, Maven commands, test matrix (Java 11/17, GraalVM 17/21)
  - Code guidelines: compilation targets, testing requirements, cross-platform compatibility
  - Task categorization: suitable tasks for Copilot vs. human-required architectural changes
  - Security best practices and documentation standards
  - Links to project resources and communication channels

## Context

The instructions align with actual build configuration (`maven.compiler.source=11` in pom.xml) and CI matrix (Linux/macOS/Windows on Java 11/17).

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

- Fixes nitrite/nitrite-java#1176

<!-- START COPILOT CODING AGENT TIPS -->
---

💬 We'd love your input! S

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
