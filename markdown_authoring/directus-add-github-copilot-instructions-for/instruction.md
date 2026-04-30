# Add GitHub Copilot instructions for repository

Source: [directus/directus#26170](https://github.com/directus/directus/pull/26170)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

## Scope

What's changed:

- Added `.github/copilot-instructions.md` with project structure, tech stack, and development guidelines
- Documented monorepo layout (API, App, SDK, packages) and pnpm workspace configuration
- Included code quality standards, testing conventions with Vitest examples, and contributing workflow
- Added common development tasks, package management patterns, and security/performance guidelines

## Potential Risks / Drawbacks

- None - this is documentation only

## Tested Scenarios

- Validated Prettier formatting compliance

## Review Notes / Questions

- Special attention should be paid to accuracy of documented commands and project structure

## Checklist

- [ ] Added or updated tests
- [x] Documentation PR created [here](https://github.com/directus/docs) or not required

---

Fixes #<num>

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

- Fixes directus/directus#26169

<!-- START COPILOT CODING AGENT TIPS -->
---

✨ Let Copilot co

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
