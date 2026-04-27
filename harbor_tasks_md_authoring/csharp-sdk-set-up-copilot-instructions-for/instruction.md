# ✨ Set up Copilot instructions for repository

Source: [modelcontextprotocol/csharp-sdk#858](https://github.com/modelcontextprotocol/csharp-sdk/pull/858)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

This PR adds comprehensive GitHub Copilot instructions to help contributors and Copilot generate code that aligns with the repository's conventions and best practices, with a focus on library implementation rather than consumption.

## What's Changed

Added `.github/copilot-instructions.md` with detailed guidance covering:

- **Critical Build and Test Requirements**: Prominent section emphasizing that building and testing are mandatory steps before declaring any task complete, with explicit workflow instructions
- **Project Overview**: Documentation of the three main packages (ModelContextProtocol.Core, ModelContextProtocol, and ModelContextProtocol.AspNetCore) and their dependencies
- **C# Coding Standards**: File-scoped namespaces, implicit usings, nullable reference types, preview language features, and editorconfig conventions
- **Architecture Patterns**: Dependency injection patterns, JSON serialization with System.Text.Json (including AOT support), async/await best practices, MCP protocol implementation guidelines, and error handling
- **Key Types and Architectural Layers**: Comprehensive documentation of the SDK's architectural organization including:
  - Protocol Layer with DTO types in the `Protocol/` folder
  - Built-in JSON-RPC 2.0 implementation with polymorphic message conversion
  - ITransport abstraction and TransportBase
  - McpSession, McpServer, and McpClient types and their relationships
  - Two transport implementations (Stdio-based and HTTP-based) with th

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
