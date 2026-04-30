# Update CLAUDE.md with concise testing commands for optional dependencies and extras

Source: [mlflow/mlflow#17749](https://github.com/mlflow/mlflow/pull/17749)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

This PR enhances the testing documentation in CLAUDE.md by adding concise examples for running tests with optional dependencies and project extras using UV's `--with` and `--extra` flags.

## What's Added

Added two simple examples to the existing Testing section:

```bash
# Run tests with optional dependencies/extras
uv run --with transformers pytest tests/transformers
uv run --extra gateway pytest tests/gateway
```

## Why This Matters

Previously, developers had to manually figure out which dependencies were needed to test specific MLflow components. This documentation now provides:

- **Clear guidance** on testing transformers and gateway components (as specifically requested)
- **Practical examples** integrated into the existing documentation structure
- **Validated examples** - all commands were tested to ensure they work correctly
- **Better developer experience** for contributors working on different parts of MLflow

This makes it much easier for contributors to run tests for the specific components they're working on without having to install all possible dependencies. The approach is concise and maintainable while providing the essential information developers need.

<!-- START COPILOT CODING AGENT SUFFIX -->



<!-- START COPILOT CODING AGENT TIPS -->
---

💡 You can make Copilot smarter by setting up custom instructions, customizing its development environment and configuring Model Context Protocol (MCP) servers. Learn more [Copilot coding agent tips](https://gh.io

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
