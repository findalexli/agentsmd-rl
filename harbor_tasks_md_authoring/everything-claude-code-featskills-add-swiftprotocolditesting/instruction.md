# feat(skills): add swift-protocol-di-testing skill

Source: [affaan-m/everything-claude-code#220](https://github.com/affaan-m/everything-claude-code/pull/220)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/swift-protocol-di-testing/SKILL.md`

## What to add / change

## Description

Adds a Swift-specific skill for protocol-based dependency injection and testing. Covers:

- **Focused protocols**: Small, single-responsibility protocols for file system, network, and external API access
- **Default + mock implementations**: Production code uses real implementations by default; tests inject mocks
- **Sendable conformance**: Patterns for safe use with Swift actors and structured concurrency
- **Swift Testing framework**: Examples using `@Test` and `#expect` macros

## Type of Change
- [x] `feat:` New feature

## Motivation

ECC currently has **zero Swift/iOS skills**. The CONTRIBUTING.md explicitly calls for "Language-specific" contributions. This skill fills a gap for the growing Swift developer community using Claude Code for iOS/macOS development.

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
  * Added comprehensive guide and examples for improving code testability through dependency injection patterns in Swift.
  * Includes production implementations and test mocks with example test scenarios.
  * Outlines best practices and anti-patterns for effective pattern applic

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
