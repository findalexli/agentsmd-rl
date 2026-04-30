# docs: add .github/copilot-instructions.md for AI coding agents

Source: [cline/cline#9606](https://github.com/cline/cline/pull/9606)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

## Summary\nAdd `.github/copilot-instructions.md` to guide AI coding agents working in this codebase.\n\n## What's included\nConcise, actionable instructions covering:\n- **Architecture overview** — Core → WebviewProvider → Controller → Task flow, CLI, and Protobuf communication\n- **Build & test commands** — Critical non-obvious commands (`npm run compile` not `build`, `npm run protos`, snapshot updates)\n- **Protobuf RPC workflow** — 4-step process for adding new RPCs\n- **Adding API providers** — Silent failure risks with proto conversion (3 required updates)\n- **Adding tools to system prompt** — Full 5+ file chain with snapshot regeneration\n- **Global state keys** — Silent `undefined` failure pattern\n- **Slash commands** — 3-place update requirement\n- **Conventions** — Path helpers, logging, feature flags\n\n## Sources\nContent synthesized from `CLAUDE.md`, `.clinerules/general.md`, `.clinerules/protobuf-development.md`, `.clinerules/cli.md`, and various README files throughout the codebase.
<!-- ELLIPSIS_HIDDEN -->

----

> [!IMPORTANT]
> Adds `.github/copilot-instructions.md` to guide AI coding agents with architecture, build/test commands, and feature addition workflows.
> 
>   - **Documentation**:
>     - Adds `.github/copilot-instructions.md` for AI coding agents.
>     - Includes architecture overview, build/test commands, and workflows for Protobuf RPC, API providers, and tools.
>   - **Architecture**:
>     - Describes core components: `extension.ts`, `Webview

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
