# add custom SKILL.md

Source: [langchain-ai/docs#3757](https://github.com/langchain-ai/docs/pull/3757)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `src/.mintlify/skills/deep-agents/SKILL.md`
- `src/.mintlify/skills/langchain/SKILL.md`
- `src/.mintlify/skills/langgraph/SKILL.md`
- `src/.mintlify/skills/langsmith/SKILL.md`

## What to add / change

Fixes DOC-641

Add custom skill.md files for AI agent discovery across all four products (LangSmith, LangChain, LangGraph, Deep Agents) using Mintlify's .mintlify/skills/ multi-skill directory, so AI agents can discover and selectively load product-specific capabilities via /.well-known/agent-skills/index.json.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
