# Add AGENTS.md

Source: [microsoft/mcp#536](https://github.com/microsoft/mcp/pull/536)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## What does this PR do?

AGENTS.md is quickly becoming the defacto for communicating to agents information about the application.  Coding practices, standards, tips, guides, to help the model better understand and take appropriate action.  

It is similar to .github/copilot-instructions.md, but works with any IDE or AI Dev Tool.  Claude Code, Cursor, etc.


More info: https://github.com/openai/agents.md/

## GitHub issue number?
`[Link to the GitHub issue this PR addresses]`

## Pre-merge Checklist
- [ ] Required for All PRs
    - [ ] **Read [contribution guidelines](https://github.com/microsoft/mcp/blob/main/CONTRIBUTING.md)**
    - [ ] PR title clearly describes the change
    - [ ] Commit history is clean with descriptive messages ([cleanup guide](https://github.com/Azure/azure-powershell/blob/master/documentation/development-docs/cleaning-up-commits.md))
    - [ ] Added comprehensive tests for new/modified functionality
    - [ ] Updated `servers/Azure.Mcp.Server/CHANGELOG.md` and/or `servers/Fabric.Mcp.Server/CHANGELOG.md` for product changes (`features, bug fixes, UI/UX, updated dependencies`)
- [ ] For MCP tool changes:
    - [ ] **One tool per PR**: This PR adds or modifies only one MCP tool for faster review cycles
    - [ ] Updated `servers/Azure.Mcp.Server/README.md` and/or `servers/Fabric.Mcp.Server/README.md` documentation
    - [ ] Updated command list in `/docs/azmcp-commands.md` and/or `/docs/fabric-commands.md`
    - [ ] For new or mod

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
