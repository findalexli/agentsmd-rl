The matplotlib repository currently lacks a `CLAUDE.md` file in its root directory. This file is used by AI coding assistants (such as Claude Code) to understand repository-specific conventions, build instructions, testing guidelines, and other task-specific guidance that helps contributors work more effectively on the codebase.

Without this file, an AI assistant working on matplotlib issues will not be aware of important project-specific settings and workflows. This can lead to suboptimal or incorrect contributions, particularly around matplotlib's rendering and testing infrastructure.

Your job is to create a `CLAUDE.md` file in the root of the repository that provides task-specific guidance for working on matplotlib fixes. The file is a standard Markdown document.

The file must include guidance about using the "Agg" backend when running tests. The Agg backend is matplotlib's non-interactive renderer that renders to a pixel buffer without requiring a display. It is the standard choice for running matplotlib tests in headless environments (CI, Docker containers, remote servers) because it avoids dependencies on GUI frameworks like Tk, Qt, or GTK, and it produces deterministic, cross-platform output. Telling contributors to use the Agg backend helps prevent test failures caused by missing display environments or GUI library mismatches.

The file should be structured as a Markdown document with a level-1 heading that reads "Task-specific guidance". The guidance about the Agg backend should appear in the body of the document below this heading.

## Requirements

- The file must be named `CLAUDE.md` and placed in the repository root directory
- The file must use valid Markdown syntax
- The content must be placed under a level-1 heading with the text "Task-specific guidance"
- The body must include a statement recommending or explaining the use of the Agg backend for tests

## Code Style Requirements

- The repository uses `ruff` for Python linting and formatting. Run `ruff check lib/matplotlib --output-format concise` to verify lint compliance
- Python imports should follow standard conventions (`import matplotlib`, `import matplotlib.pyplot as plt`)

## Context

Matplotlib is a comprehensive library for creating static, animated, and interactive visualizations in Python. The repository is a large, mature codebase with many contributors. A well-crafted CLAUDE.md helps ensure that automated tooling and AI assistants contribute changes that are consistent with the project's conventions and testing practices.
