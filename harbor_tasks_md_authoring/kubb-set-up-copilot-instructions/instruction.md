# Set up Copilot instructions

Source: [kubb-labs/kubb#2055](https://github.com/kubb-labs/kubb/pull/2055)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Adds `.github/copilot-instructions.md` to configure GitHub Copilot for this repository per [best practices](https://gh.io/copilot-coding-agent-tips).

### Changes

- Created `.github/copilot-instructions.md` with repository-specific guidance derived from existing `AGENTS.md`:
  - Repository overview (monorepo, ESM-only, Node 20, pnpm/Turborepo)
  - Setup and build commands
  - Code style conventions (quotes, naming, TypeScript)
  - PR guidelines
  - Plugin architecture overview with `definePlugin` example
  - Component and generator locations

References the detailed `AGENTS.md` for comprehensive architecture documentation.

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

- Fixes kubb-labs/kubb#2054

<!-- START COPILOT CODING AGENT TIPS -->
---

✨ Let Copilot coding agent [set things up for you](https://github.com/kubb-labs/kubb/issues/new?title=✨+Set+up+Copilot+instructions&body=Configure%20instructions%20for%20this%20repository%20as%20documented%20in%20%5BB

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
