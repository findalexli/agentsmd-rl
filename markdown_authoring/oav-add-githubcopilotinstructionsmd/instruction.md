# Add .github/copilot-instructions.md

Source: [Azure/oav#1202](https://github.com/Azure/oav/pull/1202)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Adds Copilot coding agent instructions per [best practices](https://gh.io/copilot-coding-agent-tips).

Covers:
- **Build/lint/test commands** — `npm ci`, `npm run build`, `npm run lint`, `npm test`, `npm run fast-test`
- **Coding conventions** — Prettier (semicolons, 100-char width), ESLint import ordering, simple array syntax (`string[]`)
- **Language/framework context** — TypeScript strict mode, CommonJS, Node ≥20, inversify DI
- **Testing** — Jest + ts-jest, test file naming/location patterns
- **Project structure** — `lib/`, `test/`, `dist/`, `documentation/`, `regression/`, `eng/`

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

- Fixes Azure/oav#1201

<!-- START COPILOT CODING AGENT TIPS -->
---

💬 We'd love your input! Share your thoughts on Copilot coding agent in our [2 minute survey](https://gh.io/copilot-coding-agent-survey).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
