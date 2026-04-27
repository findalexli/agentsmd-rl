# chore(docs): add AGENTS.md for dynamodb-mcp-server

Source: [awslabs/mcp#2072](https://github.com/awslabs/mcp/pull/2072)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `src/dynamodb-mcp-server/AGENTS.md`

## What to add / change

<!-- markdownlint-disable MD041 MD043 -->
Fixes

## Summary
https://agents.md/

### Changes
Added AGENTS.md file to provide AI coding agents with structured, machine-readable instructions for working with the AWS DynamoDB MCP Server project. The file includes setup commands, code style guidelines, testing procedures, environment configuration, project structure documentation, and development workflow guidance.

### User experience

Before: AI coding agents had no standardized documentation to understand project setup, dependencies, testing procedures, or development workflows, leading to inconsistent and potentially incorrect assistance.

After: AI coding agents can reference AGENTS.md for accurate, factual information about:

- Exact setup commands using uv
- Code style configuration (Ruff, Pyright)
- Testing procedures and available test files
- Environment variables and MCP configuration
- Project structure and component descriptions

## Checklist

If your change doesn't seem to apply, please leave them unchecked.

* [x] I have reviewed the [contributing guidelines](https://github.com/awslabs/mcp/blob/main/CONTRIBUTING.md)
* [x] I have performed a self-review of this change
* [x] Changes have been tested
* [x] Changes are documented

Is this a breaking change? (Y/N) N

**RFC issue number**:

Checklist: N/A

* [ ] Migration process documented
* [ ] Implement warnings (if it can live side by side)

## Acknowledgment

By submitting thi

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
