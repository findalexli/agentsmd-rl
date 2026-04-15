# Make MCP terminal modal states skill-friendly

## Problem

The Playwright MCP terminal commands use hyphenated names (`key-press`, `key-down`, `mouse-move`, etc.) that feel unnatural in skill/daemon mode. Additionally, the `eval` command requires users to write full arrow function syntax even for simple expressions.

When the CLI runs in daemon/skill mode, modal state messages (dialog prompts, file chooser notifications) reference internal MCP tool names — users in skill mode should see human-friendly skill command names instead.

## Goals

1. **Commands should use skill-friendly names**: The terminal command declarations and CLI help text should use shorter, natural names without hyphens.

2. **Modal state messages must adapt to skill mode**: In skill/daemon mode, modal state messages should show skill-friendly command names rather than MCP tool names. The data structure backing modal states needs to carry both identifiers.

3. **Simplify eval expressions**: The eval command should accept simple JavaScript expressions without requiring arrow function syntax; it should auto-detect and wrap plain expressions.

4. **Document the CLI commands**: Create a `SKILL.md` file in the terminal directory that documents all available commands with examples. Update the build script so it gets copied to the output directory.

## Requirements / Acceptance Criteria

The following specifics are verified by the test suite and must hold true:

- **Command names in help.json**: The CLI help must use the non-hyphenated names — specifically: `press`, `keydown`, `keyup`, `mousemove`, `mousedown`, `mouseup`, `mousewheel`. The hyphenated variants (`key-press`, `key-down`, etc.) must NOT appear.

- **Skill mode modal message format**: When running in skill mode, modal state messages should display skill-friendly names like `dialog-accept or dialog-dismiss` for dialogs and `upload` for file choosers. In non-skill mode, they should show the underlying tool names (e.g., `browser_handle_dialog`, `browser_file_upload`).

- **Modal state clearedBy structure**: The `clearedBy` field on modal states must carry both the tool identifier and the skill-friendly identifier (e.g., `{ tool: "browser_handle_dialog", skill: "dialog-accept or dialog-dismiss" }`).

- **Eval auto-wrap**: Expressions passed to `eval` that do not contain `=>` should be automatically wrapped in `() => (...)` before execution.

- **SKILL.md requirements**: The file must exist in the terminal directory, include valid YAML frontmatter with `name:` and `description:` fields, and document the new command names.

- **Build and lint must pass**: The project build and ESLint checks must complete successfully.

- **Existing test compatibility**: Modified code must remain compatible with the existing MCP test suite (including tests in `tests/mcp/`).
