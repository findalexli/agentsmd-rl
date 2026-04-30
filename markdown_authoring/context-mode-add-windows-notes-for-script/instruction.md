# Add Windows notes for script execution and path handling

Source: [mksglu/context-mode#192](https://github.com/mksglu/context-mode/pull/192)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `configs/codex/AGENTS.md`

## What to add / change

## What

Add Windows-specific notes to `AGENTS.md` covering:

* PowerShell cmdlet usage in bash-based sandbox environments
* Absolute path requirements for file operations
* MSYS2-style drive letter path conventions
* Mandatory quoting for paths with spaces

---

## Why

The sandbox executes commands using **bash (MSYS2/Git Bash)** rather than PowerShell or WSL.

Without explicit guidance, contributors frequently:

* Use PowerShell cmdlets directly → `command not found`
* Use relative paths → resolve to incorrect temp directories
* Use WSL-style `/mnt/c/...` paths → incompatible with MSYS2
* Omit quotes → path splitting bugs on Windows

These issues lead to **non-portable scripts and frequent execution failures**, especially in Codex CLI and similar environments.

---

## How

Updated `AGENTS.md` by adding a **Windows notes section** that:

1. Clarifies that sandbox shell is bash, not PowerShell
2. Enforces explicit wrapping for PowerShell commands via `pwsh`
3. Defines MSYS2 path conversion rules:

   * `C:\foo\bar` → `/c/foo/bar`
4. Requires absolute paths for all filesystem operations
5. Enforces quoting of all paths to avoid argument splitting

The goal is to make Windows behavior **explicit, deterministic, and cross-platform safe**.

---

## Affected platforms

* [ ] Claude Code
* [ ] Gemini CLI
* [ ] VS Code Copilot
* [ ] OpenCode
* [x] Codex CLI
* [x] All platforms / core MCP server

---

## TDD (required)

### RED

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
