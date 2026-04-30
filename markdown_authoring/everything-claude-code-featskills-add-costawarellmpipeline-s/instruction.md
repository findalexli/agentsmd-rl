# feat(skills): add cost-aware-llm-pipeline skill

Source: [affaan-m/everything-claude-code#219](https://github.com/affaan-m/everything-claude-code/pull/219)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/cost-aware-llm-pipeline/SKILL.md`

## What to add / change

## Description

Adds a new skill for cost-optimized LLM API usage. This skill covers four composable patterns:

- **Model Routing**: Automatically select cheaper models (Haiku) for simple tasks, reserving expensive models (Sonnet/Opus) for complex ones
- **Immutable Cost Tracking**: Track cumulative API spend with frozen dataclasses
- **Narrow Retry Logic**: Retry only on transient errors (network, rate limit), fail fast on permanent errors
- **Prompt Caching**: Cache long system prompts to reduce token costs

## Type of Change
- [x] `feat:` New feature

## Motivation

There is currently no skill in ECC that addresses LLM API cost optimization. As LLM-powered applications scale, cost control becomes critical. This skill provides battle-tested patterns extracted from production use with the Anthropic API.

## Checklist
- [x] Tests pass locally (`node tests/run-all.js`)
- [x] Validation scripts pass
- [x] Follows conventional commits format
- [x] Updated relevant documentation
- [x] Focused on one domain/technology
- [x] Includes practical code examples
- [x] Under 500 lines
- [x] Tested with Claude Code

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Documentation**
  * Added a new skill guide for cost-aware LLM pipeline patterns and best practices, covering model routing by task complexity, cost tracking mechanisms, retry strategies with exponential backoff, and prompt caching to minimize API costs. Includes pricing r

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
