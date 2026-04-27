# feat(skills): add swift-actor-persistence skill

Source: [affaan-m/everything-claude-code#221](https://github.com/affaan-m/everything-claude-code/pull/221)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/swift-actor-persistence/SKILL.md`

## What to add / change

## Description

Adds a Swift-specific skill for thread-safe data persistence using actors. Covers:

- **Actor-based repository**: Compiler-enforced thread safety with zero manual synchronization
- **In-memory cache + file persistence**: Fast reads from Dictionary cache, durable atomic writes to disk
- **Generic implementation**: Reusable across any `Codable & Identifiable` model type
- **@Observable integration**: Patterns for connecting actor repositories to SwiftUI ViewModels

## Type of Change
- [x] `feat:` New feature

## Motivation

ECC currently has no Swift/iOS skills. Swift's actor model is a modern approach to concurrency that many developers are adopting, but patterns for persistence layers are not well documented. This skill provides a ready-to-use template for offline-first iOS apps.

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
  * Added comprehensive guide for Swift actor-based persistence pattern, covering thread-safe data management, practical examples, best practices, and anti-patterns for developers implementing persistent storage.

<!-- end of auto-generated comment: release notes by

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
