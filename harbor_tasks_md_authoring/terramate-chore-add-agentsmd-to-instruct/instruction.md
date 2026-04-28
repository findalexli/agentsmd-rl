# chore: add agents.md to instruct ai coding agents

Source: [terramate-io/terramate#2240](https://github.com/terramate-io/terramate/pull/2240)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Adds an [AGENTS.md](https://agents.md/) to the project which can be used to provide better context about the project to IDEs such as Cursor or Claude.

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> Adds `AGENTS.md` documenting project overview, setup, code style, LSP development/testing guidelines, and contributor practices for AI agents.
> 
> - **Docs**:
>   - Add `AGENTS.md` providing guidance for AI coding agents.
>     - Project overview and repo structure (`/cmd/`, `/ls/`, `/hcl/`, etc.).
>     - Setup/build/test/lint commands and development workflow.
>     - Go code style, error/logging/testing patterns.
>     - Language server (`/ls/`) architecture, key files, and testing patterns.
>     - Terramate concepts (namespaces, imports, overrides) and implementation details.
>     - Performance, pitfalls (HCL/LSP coords, imports), and security considerations.
>     - PR checklist, review guidelines, debugging tips, and references.
> 
> <sup>Written by [Cursor Bugbot](https://cursor.com/dashboard?tab=bugbot) for commit b17858754a0f8e3405717ebbcace75d340faf73e. This will update automatically on new commits. Configure [here](https://cursor.com/dashboard?tab=bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
