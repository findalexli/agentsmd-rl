# feat(skills): add regex-vs-llm-structured-text skill

Source: [affaan-m/everything-claude-code#223](https://github.com/affaan-m/everything-claude-code/pull/223)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/regex-vs-llm-structured-text/SKILL.md`

## What to add / change

## Description

Adds a skill for deciding between regex and LLM when parsing structured text. Provides a hybrid pipeline pattern:

- **Decision framework**: When to use regex vs LLM (flowchart-based)
- **Confidence scoring**: Programmatically flag low-confidence regex extractions
- **Hybrid pipeline**: Regex handles 95-98%, LLM validates only edge cases
- **Real-world metrics**: 95% cost savings vs all-LLM approach

## Type of Change
- [x] `feat:` New feature

## Motivation

Many developers default to LLM for all text parsing, which is expensive and slow. This skill provides a practical framework for combining regex and LLM efficiently — a pattern applicable to quiz parsing, form extraction, invoice processing, and document structure parsing.

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

## Documentation
* Added guide for parsing structured text using a regex-first approach enhanced with LLM validation for edge cases, including architectural patterns, scoring logic, best practices, and usage scenarios for form extraction, quizzes, invoices, and other structured data.

<!-- end of auto-generated comment: release notes by c

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
