# Set up Copilot coding agent instructions

Source: [storybookjs/storybook#33887](https://github.com/storybookjs/storybook/pull/33887)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Adds `.github/copilot-instructions.md` to configure GitHub Copilot coding agent behavior for this repository, following the [best practices guide](https://gh.io/copilot-coding-agent-tips).

## What's included

- **Repo structure** — monorepo layout, key directories, and what to ignore
- **Build & test commands** — `yarn task` vs NX equivalents, required flags (`-c production`), and approximate runtimes
- **Commands to avoid** — `yarn task dev` / `yarn start` (run indefinitely)
- **Sandbox environments** — location change (`../storybook-sandboxes/`), available templates, and fallback workflow when sandbox generation fails
- **Development workflows** — per-change-type guidance (code, UI, addon/framework)
- **Contributing guidelines** — logging conventions (`node-logger` vs `client-logger`), test coverage expectations, code quality checks (Prettier + ESLint)

Also fixes the Yarn version in the instructions (`4.9.1` → `4.10.3`) to match the actual `packageManager` field in `package.json`.

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
> ## Comments on the Issue (you are @

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
