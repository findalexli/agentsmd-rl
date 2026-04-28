# Docs: Update CLAUDE.md to reflect current architecture

Source: [ENTERPILOT/GoModel#71](https://github.com/ENTERPILOT/GoModel/pull/71)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

The file was significantly outdated, missing many components added since the initial version. Expanded from 85 to 176 lines covering: guardrails pipeline, audit logging, usage tracking, unified storage, llmclient with retries/circuit breaker, error handling patterns, full middleware stack, startup/shutdown sequences, config cascade, all make targets, integration and contract tests, and configuration reference.

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Documentation**
  * Updated architecture documentation with expanded provider support and operational guidance
  * Added Ollama as a supported provider alongside existing integrations
  * Enhanced documentation for configuration, error handling, testing procedures, and system observability

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
