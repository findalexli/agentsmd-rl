# docs(skills): add creating-dotnet-mcp-servers skill

Source: [SebastienDegodez/copilot-instructions#13](https://github.com/SebastienDegodez/copilot-instructions/pull/13)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/skills/creating-dotnet-mcp-servers/SKILL.md`
- `.github/skills/creating-dotnet-mcp-servers/references/advanced.md`
- `.github/skills/creating-dotnet-mcp-servers/references/error-handling.md`
- `.github/skills/creating-dotnet-mcp-servers/references/testing.md`

## What to add / change

<!-- 
Thanks for creating this pull request 🤗

Please make sure that the pull request is limited to one type (docs, feature, etc.) and keep it as small as possible. You can open multiple prs instead of opening a huge one.
-->

<!-- If this pull request closes an issue, please mention the issue number below -->
Closes # <!-- Issue # here -->

## 📑 Description
This pull request introduces a new skill guide and comprehensive testing reference for building and testing Model Context Protocol (MCP) servers in .NET. The main changes include a detailed skill documentation for creating MCP servers, including setup, transport configuration, error handling, and common mistakes, as well as a thorough reference guide for testing MCP servers with integration, unit, and containerized tests.

Skill documentation for MCP server creation:

* Added `.github/skills/creating-dotnet-mcp-servers/SKILL.md` with step-by-step instructions for building MCP servers in .NET, including package installation, AOT serialization, tool implementation patterns, transport configuration (SSE/stdio), and error handling.
* Included quick reference tables, common mistake fixes, and links to advanced topics and MCP specification for further reading.

Testing reference for MCP servers:

* Added `.github/skills/creating-dotnet-mcp-servers/references/testing.md` with detailed guides for integration tests using `WebApplicationFactory` and `SseClientTransport`, unit tests for tool logic, and test organi

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
