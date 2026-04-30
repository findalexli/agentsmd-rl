# Add GitHub Copilot instructions for repository

Source: [orbat-mapper/orbat-mapper#316](https://github.com/orbat-mapper/orbat-mapper/pull/316)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Configures `.github/copilot-instructions.md` to provide the Copilot coding agent with repository context and conventions.

## Changes

- **Project context**: Vue 3 + TypeScript + Vite stack, OpenLayers mapping, military symbology focus
- **Build/test commands**: pnpm-based workflow (install, dev, build, test:unit, format, type-check)
- **Code standards**: Composition API with `<script setup>`, strict TypeScript, Prettier @ 90 chars, `@/` path alias
- **File organization**: Component/store/composable locations, module structure
- **Testing patterns**: Vitest with `.test.ts` files, describe/it/expect conventions
- **Key dependencies**: OpenLayers, Turf.js, Pinia, milsymbol, Immer for immutability
- **UI components**: shadcn-vue component library with Lucide icons, Tailwind CSS styling
- **Domain notes**: Map performance considerations, accessibility requirements

Follows GitHub's best practices for coding agent configuration.

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


</

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
