# Add GitHub Copilot instructions for repository

Source: [tikmatrix/tikmatrix-desktop#81](https://github.com/tikmatrix/tikmatrix-desktop/pull/81)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Configures Copilot coding agent instructions per [GitHub best practices](https://gh.io/copilot-coding-agent-tips).

## Changes

- **Created `.github/copilot-instructions.md`** with:
  - Project architecture (Tauri v1 + Vue 3, daisyUI + Tailwind CSS)
  - Coding standards (simplicity first, minimal changes, English comments/Chinese responses)
  - i18n requirements (EN/CN/RU support mandatory)
  - Build/dev/lint commands from package.json
  - File naming conventions (PascalCase for Vue, camelCase for JS, kebab-case for config)
  - Ecosystem context (agent, Android app, admin backend, website)
  - Security and performance guidelines
  - Common task workflows

The instructions align with existing `AGENTS.md` conventions and provide Copilot with repository-specific context for code generation and reviews.

<!-- START COPILOT ORIGINAL PROMPT -->



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



<!-- START COPILOT CODING AGENT SUFFIX -->

- Fixes tikmatrix/tikmatrix-desktop#80

<!-- START COPILOT CODING AGENT

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
