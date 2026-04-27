# feat(skills): add content-hash-cache-pattern skill

Source: [affaan-m/everything-claude-code#222](https://github.com/affaan-m/everything-claude-code/pull/222)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/content-hash-cache-pattern/SKILL.md`

## What to add / change

## Description

Adds a Python skill for caching expensive file processing results using SHA-256 content hashes. Covers:

- **Content-hash cache keys**: File content (not path) determines cache identity — survives renames/moves
- **Frozen dataclass entries**: Immutable cache entries with manual JSON serialization
- **Service layer separation**: Processing functions stay pure; caching is a separate wrapper (SRP)
- **Graceful corruption handling**: Invalid cache entries are treated as misses, never crashes

## Type of Change
- [x] `feat:` New feature

## Motivation

File processing pipelines (PDF parsing, OCR, text extraction) are expensive. This pattern provides a reusable, path-independent caching strategy that integrates cleanly with existing code without modifying processing functions.

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
  * Added documentation for a content-hash cache pattern for file processing, covering implementation strategies, error handling, design decisions, and usage guidelines.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
