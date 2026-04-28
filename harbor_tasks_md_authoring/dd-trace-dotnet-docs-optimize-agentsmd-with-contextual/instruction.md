# [Docs] Optimize `AGENTS.md` with contextual load guidance

Source: [DataDog/dd-trace-dotnet#7625](https://github.com/DataDog/dd-trace-dotnet/pull/7625)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary of changes

Optimizes `AGENTS.md` as a navigation hub for AI agents with explicit "📖 Load when..." guidance for each detailed documentation reference. Reduces file size by 32% (27 KB → 18.4 KB) while maintaining sufficient context for intelligent decision-making.

## Reason for change

AI agents need clear signals about:
1. **When** to load additional documentation files (to avoid unnecessary token consumption)
2. **What** each file contains (to make informed loading decisions)
3. **Enough context** in the main file to understand the codebase structure without loading everything

The previous `AGENTS.md` had duplicated content from `docs/development/` files, making it inefficient for AI agents to navigate.

## Implementation details

### Structural Improvements for AI Agents

1. **Added explicit AI agent guidance** at the top of the file
2. **Added "📖 Load when..." sections** before each detailed doc reference with:
   - Clear trigger conditions (e.g., "when creating a new integration")
   - Brief description of what the detailed doc contains
   - Context about when NOT to load the file

3. **Reorganized content into clear sections**:
   - **Build & Development** — Quick start + reference to tracer/README.MD for details
   - **Creating Integrations** — Quick reference + load guidance for AutomaticInstrumentation.md and DuckTyping.md
   - **Azure Functions & Serverless** — Quick reference + load guidance for platform-specific docs
   - **C

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
