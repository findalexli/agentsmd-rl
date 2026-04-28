# docs: Add PR title format documentation to copilot-instructions

Source: [Quantco/dataframely#249](https://github.com/Quantco/dataframely/pull/249)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Documents Conventional Commits PR title requirements in `.github/copilot-instructions.md` to align with existing CI enforcement in `.github/workflows/chore.yml`.

## Changes

- Added "Pull request titles (required)" subsection under "When Making Changes"
- Documented format: `<type>[!]: <Subject>`
- Listed all 11 allowed commit types (feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert)
- Specified rules for breaking changes (`!`) and subject formatting (uppercase start, no trailing `.` or space)
- No scopes mentioned (not enforced by CI)

Positioned after the existing 5-item checklist to maintain logical flow from code changes to PR conventions.

<!-- START COPILOT ORIGINAL PROMPT -->



<details>

<summary>Original prompt</summary>

> Create a PR in `Quantco/dataframely` (base branch `main`) that updates the existing file `.github/copilot-instructions.md`.
> 
> ### Change requested
> Add a new section under **"## When Making Changes"**, placed **after** the existing numbered checklist items (after item 5: "API changes").
> 
> Insert the following subsection exactly (no mentions of scopes):
> 
> - Heading: `### Pull request titles (required)`
> - Text describing Conventional Commits PR title format: ``<type>[!]: <Subject>``
> - List of allowed `type` values with descriptions:
>   - `feat`: A new feature
>   - `fix`: A bug fix
>   - `docs`: Documentation only changes
>   - `style`: Changes that do not affect the meaning of the code (white-space, formatting,

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
