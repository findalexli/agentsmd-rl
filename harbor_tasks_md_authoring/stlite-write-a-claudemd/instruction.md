# Write a CLAUDE.md

Source: [whitphx/stlite#1765](https://github.com/whitphx/stlite/pull/1765)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Add detailed documentation for AI assistants working on the stlite codebase:
- Complete project overview and architecture
- Repository structure and monorepo organization
- Development workflows and build system details
- Package reference with all 11 workspace packages
- Testing strategies (Vitest, Playwright, pytest)
- Code conventions and style guides
- Common development tasks and examples
- Critical constraints and gotchas specific to Pyodide/WebAssembly
- Troubleshooting guide for common issues

This guide covers the Streamlit integration architecture, worker-based runtime, Python wheel compilation, and all the unique constraints of running Python in the browser via Pyodide.

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Documentation**
  * Added comprehensive developer guide documenting project structure, architecture, build system, testing strategies, and development workflows.

<sub>✏️ Tip: You can customize this high-level summary in your review settings.</sub>

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
