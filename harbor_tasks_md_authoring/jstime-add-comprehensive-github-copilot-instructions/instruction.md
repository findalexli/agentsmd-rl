# Add comprehensive GitHub Copilot instructions for improved developer efficiency

Source: [jstime/jstime#323](https://github.com/jstime/jstime/pull/323)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

This PR adds a comprehensive `.github/copilot-instructions.md` file to help GitHub Copilot provide more accurate and context-aware code suggestions when working on the jstime project.

## What's included

The copilot instructions file provides detailed guidance on:

- **Project Architecture**: Overview of jstime as a Rust-based JavaScript runtime using V8, with details about the core library (`jstime_core`) and CLI structure
- **Coding Standards**: Rust 2021 conventions, formatting with `cargo fmt`, linting with `cargo clippy`, and code style guidelines
- **V8 Integration Patterns**: Common patterns for working with V8 including scope management, external functions, isolate state, and memory management
- **Built-in APIs**: Documentation of the built-in JavaScript APIs (console, timers, fetch, URL, performance, microtask) and step-by-step guide for adding new ones
- **Testing Guidelines**: Test organization, patterns with examples, and how to run tests
- **Build & CI Requirements**: Local development commands and CI validation steps
- **Module System & Event Loop**: Details about ES modules support and async operation handling
- **Best Practices**: Project-specific guidelines emphasizing minimalism, spec compliance, performance, and API stability

## Benefits

With these instructions, GitHub Copilot will better understand:
- The project's V8-based architecture and how to work with V8 APIs
- Rust coding conventions specific to this project
- How to implement new JavaScript APIs

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
